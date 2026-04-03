from typing import Dict, Any, Optional, List
import json
from pydantic import BaseModel

from backend.db.database import db_client
from backend.db.models import UserProfile
from backend.core.profile_manager import profile_manager
from backend.core.retrieval import retrieval_engine
from backend.core.scoring import scoring_engine
from backend.core.what_if import what_if_simulator
from backend.data.loader import scheme_db
from backend.llm.client import llm_client
from backend.llm.prompts import Prompts


class ProfileUpdatesSchema(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    income: Optional[int] = None
    category: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    farmer_type: Optional[str] = None
    housing_status: Optional[str] = None
    student_class: Optional[int] = None
    marital_status: Optional[str] = None
    has_bpl_card: Optional[bool] = None
    scheme_interest: Optional[str] = None


class IntentExtractionSchema(BaseModel):
    intent: str
    profile_updates: ProfileUpdatesSchema
    query_parameters: Dict[str, Any]


class Orchestrator:
    """Progressive conversation orchestrator.
    
    Key design: Run eligibility after EVERY message, show early suggestions,
    refine results as more data comes in. Natural progressive flow.
    """

    async def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Main flow: Message → Extract → Profile → ALWAYS run eligibility → Generate response"""

        # ── 1. Fetch DB State ────────────────────────────────────────────
        profile = await db_client.get_profile(session_id)
        chat_history = await db_client.get_chat_history(session_id, limit=6)

        # ── 2. Extract Intent & Entities (LLM Call 1) ────────────────────
        extraction_prompt = (
            f"Previous chat context: {json.dumps(chat_history[-4:], ensure_ascii=False)}\n\n"
            f"User Message: {message}\n\n"
            f"Extract the intent, profile updates, and query parameters."
        )

        try:
            raw_extraction = await llm_client.generate_response(
                prompt=extraction_prompt,
                history=[{"role": "user", "content": Prompts.INTENT_EXTRACTION_SYSTEM}],
                response_schema=IntentExtractionSchema
            )
            # Clean markdown code blocks
            cleaned = raw_extraction.strip()
            for prefix in ["```json", "```"]:
                if cleaned.startswith(prefix):
                    cleaned = cleaned[len(prefix):]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]

            extraction = json.loads(cleaned.strip())
            intent = extraction.get("intent", "general_question")

            raw_updates = extraction.get("profile_updates", {})
            if hasattr(raw_updates, "model_dump"):
                raw_updates = raw_updates.model_dump(exclude_none=True)
            elif isinstance(raw_updates, dict):
                raw_updates = {k: v for k, v in raw_updates.items() if v is not None}
            profile_updates = raw_updates

            query_params = extraction.get("query_parameters", {})

        except Exception as e:
            print(f"[Orchestrator] Extraction failed: {e}")
            intent = "general_question"
            profile_updates = {}
            query_params = {}

        # ── 3. Sanitize & Update Profile ─────────────────────────────────
        if profile_updates:
            profile_updates = self._sanitize_profile_updates(profile_updates)
        if profile_updates:
            profile = profile_manager.update_profile(profile, profile_updates)
            await db_client.save_profile(profile)

        # ── 4. ALWAYS Run Eligibility (Progressive Feature) ──────────────
        # KEY RULE: Only show scheme suggestions once we have MINIMUM CONTEXT
        # Minimum = at least income OR (age + occupation) known.
        # This prevents premature suggestions with zero qualifying data.
        system_results = {}
        eligible_schemes = []
        ineligible_schemes = []
        missing_data_schemes = []

        # Determine category filter
        cat_filter = self._detect_category(profile, message, query_params)

        # We have enough context to run eligibility if:
        # - income is known, OR
        # - age is known AND occupation is known, OR
        # - user explicitly asked about eligibility/scheme
        has_min_context = (
            profile.income is not None or
            (profile.age is not None and profile.occupation is not None) or
            intent in ["check_eligibility", "ask_about_scheme"]
        )

        # Run eligibility only if we have minimum context AND not a pure greeting
        if has_min_context and intent != "greeting":
            schemes = retrieval_engine.search_schemes(
                query=query_params.get("scheme_name", ""),
                category=cat_filter
            )

            ranked_results = scoring_engine.score_and_rank(profile, schemes)

            for r in ranked_results:
                scheme_info = {
                    "scheme_id": r.scheme_id,
                    "scheme_name": r.scheme_name,
                    "eligible": r.eligible,
                    "score": r.score,
                    "failed_rules": r.failed_rules,
                    "missing_data": r.missing_data,
                    "passed_rules": r.passed_rules,
                }

                if r.eligible and len(r.failed_rules) == 0:
                    if len(r.missing_data) == 0:
                        # Fully confirmed eligible
                        eligible_schemes.append(scheme_info)
                    else:
                        # Eligible but missing some data
                        missing_data_schemes.append(scheme_info)
                elif len(r.failed_rules) <= 1 and len(r.passed_rules) > 0:
                    # Close match — only 1 failed rule, has some passes
                    ineligible_schemes.append(scheme_info)

            # Build top results for LLM context
            top_schemes = []

            # Priority: fully eligible first
            for s in eligible_schemes[:3]:
                top_schemes.append({**s, "status": "✅ Eligible"})

            # Then probably eligible (missing data only)
            for s in missing_data_schemes[:2]:
                top_schemes.append({**s, "status": "🔄 Probably Eligible (need more info)"})

            # Only include ineligible if user specifically asked about a scheme
            if intent in ["check_eligibility", "ask_about_scheme"]:
                for s in ineligible_schemes[:2]:
                    top_schemes.append({**s, "status": "❌ Not Eligible"})

            system_results["top_schemes"] = top_schemes
            system_results["total_eligible"] = len(eligible_schemes)
            system_results["total_maybe"] = len(missing_data_schemes)

        # Handle what-if scenario
        if intent == "what_if":
            overrides = query_params.get("what_if_overrides", {})
            if overrides:
                sim_results = what_if_simulator.run_simulation(profile, overrides)
                top_sim = []
                for r in sim_results[:4]:
                    status_text = "✅ Eligible" if r.eligible else "❌ Not Eligible"
                    top_sim.append({
                        "scheme_id": r.scheme_id,
                        "scheme_name": r.scheme_name,
                        "status": status_text,
                        "failed_reasons": r.failed_rules,
                        "missing_data": r.missing_data,
                    })
                system_results["what_if_results"] = top_sim

        # Handle scheme detail request
        if intent == "ask_about_scheme":
            scheme_name_query = query_params.get("scheme_name", message)
            detail = self._find_scheme_detail(scheme_name_query, profile)
            if detail:
                system_results["scheme_detail"] = detail

        # ── 5. Smart Context-Aware Missing Fields ────────────────────────
        missing_fields_objs = profile_manager.get_missing_fields(profile, max_questions=2)
        missing_fields = [m.field for m in missing_fields_objs]

        # ── 6. Determine Conversation Phase ──────────────────────────────
        completeness = profile_manager.get_profile_completeness(profile)
        conversation_phase = self._determine_phase(profile, completeness, len(chat_history), intent)

        # ── 7. Generate Natural Response (LLM Call 2) ────────────────────
        history_text = ""
        if chat_history:
            for h in chat_history[-4:]:
                role_label = "Citizen" if h["role"] == "user" else "Samarth"
                history_text += f"{role_label}: {h['content']}\n"

        # What is the single MOST IMPORTANT field to ask next?
        next_question = ""
        if missing_fields_objs and conversation_phase not in ["detail", "refined_results"]:
            next_question = missing_fields_objs[0].question  # Only one!

        # Phase-specific instruction
        phase_instruction = self._get_phase_instruction(
            conversation_phase, intent, system_results, profile, completeness
        )

        # Eligible scheme summary for easy LLM reference
        eligible_summary = ""
        top_schemes = system_results.get("top_schemes", [])
        fully_eligible = [s for s in top_schemes if "✅" in s.get("status", "")]
        probably_eligible = [s for s in top_schemes if "🔄" in s.get("status", "")]

        if fully_eligible:
            eligible_summary = "CONFIRMED ELIGIBLE SCHEMES:\n"
            for s in fully_eligible:
                eligible_summary += f"  - {s['scheme_name']}\n"
        if probably_eligible:
            eligible_summary += "PROBABLY ELIGIBLE (need more info):\n"
            for s in probably_eligible:
                eligible_summary += f"  - {s['scheme_name']} (missing: {', '.join(s.get('missing_data', []))})\n"

        generation_prompt = f"""CONVERSATION SO FAR:
{history_text if history_text else "(This is the very first message)"}

USER'S LATEST MESSAGE: "{message}"
INTENT: {intent}

USER PROFILE (what we know so far):
  Name: {profile.name or "unknown"}
  Age: {profile.age or "unknown"}
  Gender: {profile.gender or "unknown"}
  Annual Income: {"Rs. " + str(profile.income) if profile.income else "unknown"}
  Category: {profile.category or "unknown"}
  Occupation: {profile.occupation or "unknown"}
  Farmer Type: {profile.farmer_type or "unknown"}
  Housing: {profile.housing_status or "unknown"}
  Student Class: {profile.student_class or "unknown"}
  Marital Status: {profile.marital_status or "unknown"}
  BPL Card: {"Yes" if profile.has_bpl_card else "No" if profile.has_bpl_card is not None else "unknown"}
  Scheme Interest: {profile.scheme_interest or "unknown"}

PHASE: {conversation_phase}

ELIGIBILITY RESULTS (from deterministic engine — NEVER contradict):
{eligible_summary if eligible_summary else "Not enough data yet to check eligibility."}

NEXT QUESTION TO ASK (ask ONLY this ONE question at the end of your response):
{next_question if next_question else "No specific question needed — wrap up or ask if they want scheme details."}

INSTRUCTION:
{phase_instruction}

Write your response now as Samarth the officer. Hinglish only. Max 5-6 lines. End with exactly 1 question."""

        response_text = await llm_client.generate_response(
            prompt=generation_prompt,
            history=[{"role": "user", "content": Prompts.RESPONSE_GENERATION_SYSTEM}]
        )

        # ── 8. Save to DB ────────────────────────────────────────────────
        await db_client.add_message(session_id, "user", message)
        await db_client.add_message(session_id, "assistant", response_text)

        # ── 9. Format final output ───────────────────────────────────────
        # Build scheme cards for frontend display
        display_schemes = []
        for s in system_results.get("top_schemes", []):
            display_status = "Eligible" if "✅" in s.get("status", "") else \
                           "Potentially Eligible" if "🔄" in s.get("status", "") else \
                           "Ineligible (or missing data)"
            display_schemes.append({
                "scheme_id": s["scheme_id"],
                "scheme_name": s["scheme_name"],
                "status": display_status,
                "failed_reasons": s.get("failed_rules", []),
                "missing_data": s.get("missing_data", []),
            })

        return {
            "session_id": session_id,
            "response": response_text,
            "profile_snapshot": profile.model_dump(),
            "schemes_evaluated": display_schemes,
            "metadata": {
                "intent": intent,
                "missing_fields": missing_fields,
                "conversation_phase": conversation_phase,
                "profile_completeness": completeness["percentage"],
            }
        }

    # ── Helper Methods ───────────────────────────────────────────────

    # Allowed values for each profile field (used for validation)
    VALID_VALUES = {
        "gender": {"male", "female", "other"},
        "category": {"sc", "st", "obc", "general", "minority"},
        "occupation": {"farmer", "fisherman", "student", "artisan", "labourer", "self_employed", "unemployed"},
        "farmer_type": {"marginal", "small", "large"},
        "housing_status": {"homeless", "kutcha_house", "pucca_house", "rented", "slum"},
        "marital_status": {"married", "unmarried", "widow", "divorced"},
        "scheme_interest": {"housing", "agriculture", "education", "employment", "women", "social_security"},
    }

    def _sanitize_profile_updates(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extracted profile updates against allowed values.
        
        This is a critical safety net: even if the LLM hallucinates
        (e.g. puts 'Student' in the gender field), we reject it here.
        """
        sanitized = {}
        for key, value in updates.items():
            if value is None or value == "":
                continue

            # Type validation
            if key == "age":
                try:
                    age = int(value)
                    if 0 < age < 150:
                        sanitized[key] = age
                    else:
                        print(f"[Sanitizer] Rejected age={value} (out of range)")
                except (ValueError, TypeError):
                    print(f"[Sanitizer] Rejected age={value} (not a number)")
                continue

            if key == "income":
                try:
                    income = int(value)
                    if income >= 0:
                        sanitized[key] = income
                    else:
                        print(f"[Sanitizer] Rejected income={value} (negative)")
                except (ValueError, TypeError):
                    print(f"[Sanitizer] Rejected income={value} (not a number)")
                continue

            if key == "student_class":
                try:
                    sc = int(value)
                    if 1 <= sc <= 12:
                        sanitized[key] = sc
                    else:
                        print(f"[Sanitizer] Rejected student_class={value} (out of 1-12)")
                except (ValueError, TypeError):
                    print(f"[Sanitizer] Rejected student_class={value} (not a number)")
                continue

            if key == "has_bpl_card":
                if isinstance(value, bool):
                    sanitized[key] = value
                elif isinstance(value, str):
                    sanitized[key] = value.lower() in ("true", "yes", "1", "haan", "ha")
                continue

            if key == "name":
                # Name should be a proper noun, not an occupation
                occupation_words = {"farmer", "fisherman", "student", "artisan", "labourer", "worker"}
                if isinstance(value, str) and value.strip().lower() not in occupation_words and len(value.strip()) > 0:
                    sanitized[key] = value.strip()
                else:
                    print(f"[Sanitizer] Rejected name={value} (looks like an occupation, not a name)")
                continue

            # Enum validation for string fields
            if key in self.VALID_VALUES:
                if isinstance(value, str):
                    normalized = value.strip().lower()
                    if normalized in self.VALID_VALUES[key]:
                        # Preserve original casing for category (SC, ST, OBC)
                        if key == "category":
                            sanitized[key] = normalized.upper() if normalized in {"sc", "st", "obc"} else normalized.title()
                        else:
                            sanitized[key] = normalized
                    else:
                        print(f"[Sanitizer] Rejected {key}={value} (not in {self.VALID_VALUES[key]})")
                continue

            # Pass through any other fields unchanged (e.g. scheme_interest as-is)
            sanitized[key] = value

        print(f"[Sanitizer] Input: {updates} → Output: {sanitized}")
        return sanitized

    def _detect_category(self, profile: UserProfile, message: str, query_params: Dict) -> Optional[str]:
        """Auto-detect category from profile, message, or query params."""
        if profile.scheme_interest:
            return profile.scheme_interest

        combined_text = f"{message} {str(query_params)}".lower()
        category_keywords = {
            "agriculture": ["agriculture", "farming", "kisan", "krishi", "fasal", "kheti", "farmer", "khet", "zameen", "fisherman", "machhli", "machli", "matsya", "machuara", "machhua"],
            "housing": ["housing", "ghar", "awas", "home", "makan", "shelter", "kutcha", "pucca"],
            "education": ["education", "scholarship", "school", "padhai", "student", "class", "vidyalaya", "chatravriti"],
            "women": ["women", "mahila", "ladki", "girl", "maternity", "pregnancy", "kishori", "beti"],
            "employment": ["employment", "job", "rojgar", "business", "loan", "self-employed", "artisan", "vishwakarma"],
            "social_security": ["pension", "insurance", "bima", "elderly", "disabled", "widow", "health", "ayushman", "budhapa"],
        }
        for cat, keywords in category_keywords.items():
            if any(kw in combined_text for kw in keywords):
                return cat

        # Infer from occupation
        if profile.occupation:
            occ = profile.occupation.lower()
            if occ in ("farmer", "fisherman"):
                return "agriculture"
            elif occ == "student":
                return "education"

        return None  # Will search all schemes

    def _determine_phase(self, profile: UserProfile, completeness: Dict, history_len: int, intent: str) -> str:
        """Determine conversation phase."""
        if intent == "ask_about_scheme":
            return "detail"

        if history_len <= 1:
            return "greeting"

        # We need enough data for refined results
        # Require: income + at least 2 other fields
        has_income = profile.income is not None
        filled = completeness["filled"]

        if has_income and filled >= 3:
            return "refined_results"

        if has_income or filled >= 2:
            return "early_suggestion"

        return "early_collection"

    def _get_phase_instruction(self, phase: str, intent: str, system_results: Dict, profile: UserProfile, completeness: Dict) -> str:
        """Generate precise phase-aware instructions for the LLM."""
        top_schemes = system_results.get("top_schemes", [])
        fully_eligible = [s for s in top_schemes if "✅" in s.get("status", "")]
        probably_eligible = [s for s in top_schemes if "🔄" in s.get("status", "")]
        eligible_count = system_results.get("total_eligible", 0)

        if phase == "greeting":
            return (
                "GREETING PHASE. "
                "Say: 'Namaste! Main Samarth hoon 😊' "
                "Then ask their name AND what type of scheme they want to know about. "
                "Keep it to 2-3 lines ONLY. Nothing else."
            )

        if phase == "early_collection":
            # Not enough data for eligibility yet
            return (
                "COLLECTING INFO PHASE. "
                "We don't have enough info to suggest schemes yet. "
                "Acknowledge what the user just shared (name, occupation, etc.) warmly in 1 line. "
                "Then naturally ask the ONE next most important question. "
                "Example: If they said 'main kisaan hoon', say 'Namaste [name] ji 🙏 Achha, kheti se judi madad chahte hain 👍' "
                "then ask: 'Aapki approx saalana income kitni hai?' "
                "DO NOT mention any scheme names yet. DO NOT suggest anything yet. Just collect data."
            )

        if phase == "early_suggestion":
            if fully_eligible:
                scheme = fully_eligible[0]
                return (
                    f"EARLY SUGGESTION PHASE. "
                    f"We found a match! The user is eligible for: {scheme['scheme_name']}. "
                    f"Start with 'Theek hai 👍' then say: "
                    f"'Abhi tak ki jankari ke basis par aap **{scheme['scheme_name']}** ke liye eligible lag rahe hain.' "
                    f"Give 1-line benefit from the scheme data. "
                    f"Then say: 'Main aapke liye aur schemes bhi check kar sakta hoon 😊' "
                    f"Then ask the ONE next question to refine further. "
                    f"Keep it SHORT and natural."
                )
            elif probably_eligible:
                scheme = probably_eligible[0]
                return (
                    f"EARLY SUGGESTION PHASE. "
                    f"We found a probable match: {scheme['scheme_name']} but need more data. "
                    f"Acknowledge what user shared. "
                    f"Say something like 'Laga raha hai aap {scheme['scheme_name']} ke liye eligible ho sakte hain' "
                    f"but clearly state we need more info to confirm. "
                    f"Ask the ONE next question naturally."
                )
            else:
                return (
                    "EARLY SUGGESTION PHASE — no matches yet. "
                    "Acknowledge what user shared warmly. "
                    "Say we're checking schemes and need a bit more info. "
                    "Ask the ONE next question naturally."
                )

        if phase == "refined_results":
            if top_schemes:
                scheme_list = ""
                for i, s in enumerate(top_schemes[:4], 1):
                    status_icon = "✅" if "✅" in s.get("status", "") else "🔄"
                    scheme_list += f"{i}. {s['scheme_name']} ({status_icon})\n"
                return (
                    f"REFINED RESULTS PHASE. "
                    f"We now have enough data. Show the final results clearly. "
                    f"Say: 'Bahut badhiya 👍 ab mujhe clear picture mil gaya hai' "
                    f"Then show this numbered list:\n{scheme_list}"
                    f"For each scheme: name + 1-line benefit + arrow (→). "
                    f"Then explain WHY they qualify in 1 sentence. "
                    f"List the key documents (Aadhaar, bank, land record etc). "
                    f"End with: 'Kya aap inme se kisi scheme ka poora detail dekhna chahenge?'"
                )
            else:
                return (
                    "REFINED RESULTS PHASE — no matches found. "
                    "Be supportive. Explain why no schemes matched. "
                    "Suggest what could change (income limit, category etc). "
                    "Redirect: offer to check other categories."
                )

        if phase == "detail":
            scheme_detail = system_results.get("scheme_detail")
            if scheme_detail:
                docs = [d.get('name', '') for d in scheme_detail.get('documents', [])[:4]]
                app_steps = scheme_detail.get('application', {})
                steps_text = ""
                if isinstance(app_steps, dict):
                    online = app_steps.get('online_url', '')
                    offline = app_steps.get('offline_process', '')
                    steps_text = f"Online: {online}" if online else f"Offline: {offline}"
                elif isinstance(app_steps, list):
                    steps_text = "; ".join(str(s) for s in app_steps[:3])

                return (
                    f"DETAIL PHASE. User wants full info about: {scheme_detail['name']}. "
                    f"Start with: 'Zaroor [name] ji 👍' "
                    f"Then show **{scheme_detail['name']}** as bold heading. "
                    f"Benefit: {scheme_detail.get('benefits', {})} "
                    f"Eligibility status: {scheme_detail.get('eligibility_status', '')} "
                    f"Documents needed: {', '.join(docs)} "
                    f"How to apply: {steps_text} "
                    f"End with: 'Agar aap chahein to main aapko step-by-step guide bhi de sakta hoon 😊'"
                )
            else:
                return (
                    "DETAIL PHASE — scheme not found. "
                    "Politely say you couldn't find that exact scheme. "
                    "Offer to help find schemes in their area of interest."
                )

        return "Respond naturally to the user's message. Stay in Hinglish character."

    def _find_scheme_detail(self, query: str, profile: UserProfile) -> Optional[Dict]:
        """Find a specific scheme and return full details with eligibility status."""
        all_schemes = scheme_db.get_all_schemes()
        query_lower = query.lower()

        best_match = None
        best_score = 0

        for scheme in all_schemes:
            searchable = f"{scheme.name} {scheme.name_hindi} {scheme.scheme_id}".lower()
            # Simple word overlap scoring
            query_words = set(query_lower.replace(",", "").split())
            scheme_words = set(searchable.replace(",", "").split())
            overlap = len(query_words.intersection(scheme_words))

            if overlap > best_score:
                best_score = overlap
                best_match = scheme

            # Also check if scheme_id is referenced
            if scheme.scheme_id.lower() in query_lower or query_lower in scheme.scheme_id.lower():
                best_match = scheme
                break

        if not best_match and best_score == 0:
            # Try substring match
            for scheme in all_schemes:
                if query_lower in scheme.name.lower() or query_lower in scheme.name_hindi.lower():
                    best_match = scheme
                    break

        if not best_match:
            return None

        # Check eligibility for this specific scheme
        from backend.core.eligibility_engine import eligibility_engine
        is_eligible, rule_results = eligibility_engine.check_eligibility(profile, best_match)
        failed = [r.reason for r in rule_results if r.status == "fail"]
        passed = [r.rule for r in rule_results if r.status == "pass"]
        missing = [r.rule for r in rule_results if r.status == "missing"]

        if is_eligible and len(failed) == 0 and len(missing) == 0:
            status = "✅ Aap eligible hain!"
        elif is_eligible and len(missing) > 0:
            status = f"🔄 Probably eligible (need {', '.join(missing)} info)"
        else:
            status = f"❌ Not eligible: {'; '.join(failed)}"

        return {
            "name": best_match.name,
            "name_hindi": best_match.name_hindi,
            "scheme_id": best_match.scheme_id,
            "department": best_match.department,
            "category": best_match.category,
            "description": best_match.description,
            "benefits": best_match.benefits,
            "documents": [d for d in best_match.documents_required],
            "application": best_match.application_process,
            "tags": best_match.tags,
            "eligibility_status": status,
            "passed_rules": passed,
            "failed_rules": failed,
            "missing_data": missing,
        }


orchestrator = Orchestrator()
