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

        # ── 3. Update Profile ────────────────────────────────────────────
        if profile_updates:
            profile = profile_manager.update_profile(profile, profile_updates)
            await db_client.save_profile(profile)

        # ── 4. ALWAYS Run Eligibility (Progressive Feature) ──────────────
        # This is the core innovation: even with partial data, check eligibility.
        # Show early suggestions if any scheme matches.
        system_results = {}
        eligible_schemes = []
        ineligible_schemes = []
        missing_data_schemes = []

        # Determine category filter
        cat_filter = self._detect_category(profile, message, query_params)

        # Run eligibility on ALL or filtered schemes
        if intent != "greeting" or profile.occupation or profile.scheme_interest:
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
                        eligible_schemes.append(scheme_info)
                    else:
                        missing_data_schemes.append(scheme_info)
                elif len(r.passed_rules) > 0 or len(r.missing_data) > 0:
                    # Has SOME matches or missing data — potentially relevant
                    if len(r.failed_rules) <= 1:  # Don't show if many hard fails
                        ineligible_schemes.append(scheme_info)

            # Build top results for LLM context (max 5)
            top_schemes = []

            for s in eligible_schemes[:3]:
                top_schemes.append({**s, "status": "✅ Eligible"})

            for s in missing_data_schemes[:2]:
                top_schemes.append({**s, "status": "🔄 Probably Eligible (need more info)"})

            # Only include ineligible if user specifically asked
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

        # Build smart follow-up questions
        follow_up_questions = ""
        if missing_fields_objs and conversation_phase != "detail":
            follow_up_questions = "Ask ONE of these questions naturally (pick the most relevant):\n"
            for m in missing_fields_objs[:2]:
                follow_up_questions += f"  - {m.question}\n"

        # Build phase-specific instruction
        phase_instruction = self._get_phase_instruction(
            conversation_phase, intent, system_results, profile, completeness
        )

        generation_prompt = f"""RECENT CONVERSATION:
{history_text if history_text else "(First message — citizen just arrived)"}

CITIZEN'S LATEST MESSAGE: "{message}"
DETECTED INTENT: {intent}

CITIZEN'S PROFILE:
- Name: {profile.name or "Not yet shared"}
- Age: {profile.age or "Unknown"}
- Gender: {profile.gender or "Unknown"}
- Income: {"₹" + str(profile.income) if profile.income else "Unknown"}
- Category: {profile.category or "Unknown"}
- Occupation: {profile.occupation or "Unknown"}
- Farmer Type: {profile.farmer_type or "N/A"}
- Housing: {profile.housing_status or "Unknown"}
- Student Class: {profile.student_class or "N/A"}
- Marital Status: {profile.marital_status or "Unknown"}
- BPL Card: {"Yes" if profile.has_bpl_card else "No" if profile.has_bpl_card is not None else "Unknown"}
- Scheme Interest: {profile.scheme_interest or "Not specified"}

PROFILE COMPLETENESS: {completeness['percentage']}% ({completeness['filled']}/{completeness['total']} core fields)
CONVERSATION PHASE: {conversation_phase}

═══ DETERMINISTIC SYSTEM RESULTS (NEVER contradict these) ═══
{json.dumps(system_results, indent=2, ensure_ascii=False)}

═══ FOLLOW-UP QUESTIONS ═══
{follow_up_questions if follow_up_questions else "No specific questions needed right now."}

═══ TASK ═══
{phase_instruction}

Generate a natural, warm, WhatsApp-style response. You are a real officer, not a chatbot."""

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

    def _detect_category(self, profile: UserProfile, message: str, query_params: Dict) -> Optional[str]:
        """Auto-detect category from profile, message, or query params."""
        if profile.scheme_interest:
            return profile.scheme_interest

        combined_text = f"{message} {str(query_params)}".lower()
        category_keywords = {
            "agriculture": ["agriculture", "farming", "kisan", "krishi", "fasal", "kheti", "farmer", "khet", "zameen"],
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
            if occ == "farmer":
                return "agriculture"
            elif occ == "student":
                return "education"

        return None  # Will search all schemes

    def _determine_phase(self, profile: UserProfile, completeness: Dict, history_len: int, intent: str) -> str:
        """Determine conversation phase for response generation."""
        if intent == "ask_about_scheme":
            return "detail"

        if history_len <= 1:
            return "greeting"

        if completeness["percentage"] < 40:
            return "early_collection"

        if completeness["percentage"] < 80:
            return "early_suggestion"

        return "refined_results"

    def _get_phase_instruction(self, phase: str, intent: str, system_results: Dict, profile: UserProfile, completeness: Dict) -> str:
        """Generate phase-aware instructions for the LLM."""
        top_schemes = system_results.get("top_schemes", [])
        eligible_count = system_results.get("total_eligible", 0)
        maybe_count = system_results.get("total_maybe", 0)

        if phase == "greeting":
            return (
                "This is a greeting or first message. Welcome them warmly with Johar! or Namaste!. "
                "Ask their name (if unknown). Ask how you can help. "
                "Keep it SHORT — 2-3 sentences max. Be warm and natural."
            )

        if phase == "early_collection":
            instruction = "User is sharing info. Acknowledge what they shared warmly."
            if top_schemes:
                instruction += (
                    f"\n\nIMPORTANT — EARLY SUGGESTION: {len(top_schemes)} scheme(s) already match! "
                    "Show them briefly with name + 1-line benefit. "
                    "Then say 'Main aur schemes bhi check kar sakta hoon agar aap thodi aur jankari share karein 😊' "
                    "and ask ONE follow-up question."
                )
            else:
                instruction += (
                    "\nNo schemes matched yet. Ask the follow-up question naturally "
                    "to get more data for matching. Keep it conversational."
                )
            return instruction

        if phase == "early_suggestion":
            instruction = "Profile is building up. Acknowledge the new info."
            if top_schemes:
                instruction += (
                    f"\n\nSHOW RESULTS: {eligible_count} eligible + {maybe_count} probable scheme(s). "
                    "Present them as a numbered list with short descriptions. "
                    "For eligible ones: '✅ scheme name → benefit' "
                    "Then ask if they want details on any, or ask one more question to refine."
                )
            else:
                instruction += "\nNo matching schemes yet. Suggest exploring a category or ask a refining question."
            return instruction

        if phase == "refined_results":
            instruction = "Profile is fairly complete now."
            if top_schemes:
                instruction += (
                    f"\n\nFINAL RESULTS: Show clear numbered list of {len(top_schemes)} scheme(s). "
                    "For each: name, 1-line benefit, eligibility status. "
                    "Briefly mention key documents needed for eligible ones. "
                    "Ask 'Kya aap kisi scheme ka poora detail dekhna chahenge?'"
                )
            else:
                instruction += (
                    "\nNo schemes matched. Be supportive — explain why and suggest "
                    "what would need to change. Redirect to other categories if possible."
                )
            return instruction

        if phase == "detail":
            scheme_detail = system_results.get("scheme_detail")
            if scheme_detail:
                instruction = (
                    f"User wants details about: {scheme_detail['name']}\n"
                    f"Hindi name: {scheme_detail.get('name_hindi', '')}\n"
                    f"Description: {scheme_detail.get('description', '')}\n"
                    f"Benefits: {json.dumps(scheme_detail.get('benefits', {}), ensure_ascii=False)}\n"
                    f"Documents: {json.dumps(scheme_detail.get('documents', []), ensure_ascii=False)}\n"
                    f"How to apply: {json.dumps(scheme_detail.get('application', {}), ensure_ascii=False)}\n"
                    f"Eligibility status: {scheme_detail.get('eligibility_status', 'Unknown')}\n\n"
                    "Present this in a clear, readable format:\n"
                    "1. Benefits clearly\n2. Documents as bullet list\n"
                    "3. How to apply as numbered steps\n4. Official link if available\n"
                    "End with 'Kya aur kisi scheme ke baare mein jaanna hai?'"
                )
            else:
                instruction = (
                    "User asked about a specific scheme but we couldn't find it. "
                    "Politely say you couldn't find that exact name, and offer to help "
                    "find schemes in their area of interest."
                )
            return instruction

        return "Respond naturally to the user's message based on the context above."

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
