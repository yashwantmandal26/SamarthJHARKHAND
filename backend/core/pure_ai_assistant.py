"""
Pure AI Assistant — RAG-powered conversational assistant.

Unlike the eligibility-matching orchestrator, this uses pure LLM + RAG
to answer ANY question about government schemes comprehensively.
"""

import json
import re
from typing import Dict, Any, List, Tuple
from backend.db.database import db_client
from backend.core.rag_engine import rag_engine
from backend.core.eligibility_engine import eligibility_engine
from backend.core.profile_manager import profile_manager
from backend.llm.client import llm_client


RAG_SYSTEM_PROMPT = """You are **Samarth (समर्थ)** — a senior government scheme advisor sitting at the Jharkhand Government Help Desk. You speak like a real, experienced, warm human officer helping a citizen in person.

## YOUR IDENTITY
- You are a **human officer**, NOT an AI. Never say "I'm an AI" or "As a language model."
- Your name is **Samarth** — a trusted advisor at the Jharkhand Government Help Desk.
- You speak in **warm, natural Hinglish** (Hindi + English mix). Adapt to the user's language.
- Use **"aap"** and **"ji"** respectfully. Use 1-2 relevant emojis per response (not more).
- Be warm but **professional** — like a caring senior officer.

## YOUR TWO MODES OF OPERATION

### MODE 1: PERSONALIZED SCHEME MATCHING (when user shares personal details or asks "what schemes are for me")
When a user tells you about themselves (occupation, age, income, category, etc.) or asks for personalized suggestions:
1. **If details are insufficient**, politely ask for the missing info you need:
   - Occupation (kya kaam karte hain?)
   - Approximate age
   - Annual household income
   - Category (SC/ST/OBC/General)
   - Gender
   - Any other relevant detail (BPL card, farmer type, housing, etc.)
   Ask ONLY the missing fields, not all at once. Be conversational, not like a form.
2. **Once you have enough info**, match against the ELIGIBILITY fields in the retrieved schemes
3. **Show matched schemes** in a beautiful card-like format (see SCHEME CARD FORMAT below)
4. Clearly separate "Directly Eligible" schemes from "May Also Apply" general schemes

### MODE 2: GENERAL Q&A (when user asks about a specific scheme, process, comparison, etc.)
Answer the question comprehensively using the retrieved data. Still use the scheme card format when mentioning schemes.

## SCHEME CARD FORMAT (MANDATORY when recommending/listing schemes)
When you mention any scheme, you MUST format it like this, using the LINK_ID from the retrieved data:

**1. [[Scheme Name (हिंदी नाम) →]](LINK_ID_HERE)**
- **Benefit:** ₹amount / description of benefit
- **Eligibility:** Key criteria in simple words
- **Documents:** Aadhaar, Bank Account, etc.
- **How to apply:** URL or office to visit

CRITICAL: The `[[Scheme Name →]](link_id)` format is MANDATORY. Use the exact LINK_ID value from the retrieved scheme data. Example:
- `[[PM Kisan Samman Nidhi →]](pm_kisan)` — uses the LINK_ID `pm_kisan`
- `[[Mukhyamantri Krishi Ashirwad Yojana →]](mukhyamantri_krishi_ashirwad)` — uses LINK_ID `mukhyamantri_krishi_ashirwad`

## EXAMPLE CONVERSATION FLOW

User: "I am a farmer from Jharkhand"
Samarth: "Namaste ji! 🙏 Aap kisan hain, bahut accha. Aapki kuch aur details jaan loon taaki best schemes suggest kar sakoon:
- Aapki umar lagbhag kitni hai?
- Annual income roughly kitni hai?
- Category kya hai (SC/ST/OBC/General)?
- Kya aapke paas apni zameen hai?"

User: "I am 35, income 80000, OBC, yes I have land"
Samarth: "Dhanyawaad ji! Aapki details ke hisaab se yeh schemes aapke liye bilkul sahi hain: 🎯

**1. [[Mukhyamantri Krishi Ashirwad Yojana →]](mukhyamantri_krishi_ashirwad)**
- **Benefit:** Kharif season mein input subsidy (seeds, fertilizers, machinery)
- **Eligibility:** ✅ Small/marginal farmers with cultivable land — aap eligible hain
- **Documents:** Aadhaar, land records, bank passbook

**2. [[PM Kisan Samman Nidhi →]](pm_kisan)**
- **Benefit:** ₹6,000/year (3 installments of ₹2,000)
- **Eligibility:** ✅ All farmers with cultivable land
- **How to apply:** pmkisan.gov.in → New Farmer Registration

Kisi bhi scheme par click karke poori details dekh sakte hain! Aur koi sawaal ho toh zaroor poochiye 😊"

## CRITICAL RULES
- **ONLY recommend schemes whose eligibility ACTUALLY matches the user** — check age, income, category, occupation, gender constraints
- If a scheme says "Occupation: farmer" but user is "fisherman", it is NOT relevant
- **NEVER invent** scheme names, amounts, or rules not in the data
- **NEVER dump all retrieved schemes** — filter to only relevant ones
- **NEVER output** technical fields like "LINK_ID:", "INTERNAL RELEVANCE TAG:", "Category:" to the user
- **ALWAYS use the [[Scheme Name →]](link_id) format** for every scheme mention so users can click to see full details
- Be **specific**: include exact ₹ amounts, age limits, percentages from the data
- Be **actionable**: give URLs, office names, steps the user can follow
- Be **honest**: if unsure or no match, say so clearly
- Sound like a **real human officer**, not a database"""


class PureAIAssistant:
    """RAG-powered AI assistant for comprehensive scheme information."""

    PERSONALIZATION_HINTS = {
        "for me", "for myself", "am i eligible", "eligible", "suggest", "recommend",
        "which schemes", "what schemes", "mera", "mere liye", "kaunsi yojana",
        "kaun si scheme", "profile", "match"
    }

    OCCUPATION_MAP = {
        "farmer": ["farmer", "kisan", "kisaan", "kheti", "farming", "krishi"],
        "fisherman": ["fisherman", "fishing", "machhli", "machli", "matsya", "machuara", "machhua"],
        "student": ["student", "school", "college", "padhai", "vidyarthi", "chhatra"],
        "artisan": ["artisan", "karigar", "handicraft", "craftsman", "vishwakarma"],
        "labourer": ["labourer", "laborer", "worker", "mazdoor", "majdoor", "shramik"],
        "self_employed": ["self employed", "self_employed", "business", "shop", "dukandaar", "vyapari"],
        "unemployed": ["unemployed", "berozgar", "berojgar", "jobless"],
    }

    @staticmethod
    def _extract_age(text: str) -> int | None:
        patterns = [
            r"\b(i am|i'm|my age is|age|umar|umra|old)\s*(?:about|around)?\s*(\d{1,3})\b",
            r"\b(\d{1,3})\s*(?:years?\s*old|yrs?\s*old|year|years|yrs?|saal(?:\s*ka)?|saal)\b",
        ]
        lowered = text.lower()
        for pattern in patterns:
            match = re.search(pattern, lowered)
            if match:
                age = int(match.group(match.lastindex or 1))
                if 1 <= age <= 120:
                    return age
        return None

    @staticmethod
    def _extract_income(text: str) -> int | None:
        lowered = text.lower().replace(",", "")
        lakh = re.search(r"(\d+(?:\.\d+)?)\s*lakh", lowered)
        if lakh:
            return int(float(lakh.group(1)) * 100000)

        thousand = re.search(r"(\d+(?:\.\d+)?)\s*(?:thousand|hazaar|hazar)", lowered)
        if thousand:
            return int(float(thousand.group(1)) * 1000)

        rupees = re.search(r"(?:income|rs|₹)?\s*(\d{4,9})\b", lowered)
        if rupees:
            value = int(rupees.group(1))
            if 1000 <= value <= 100000000:
                return value
        return None

    @classmethod
    def _extract_profile_updates(cls, text: str) -> Dict[str, Any]:
        lowered = text.lower()
        updates: Dict[str, Any] = {}

        age = cls._extract_age(lowered)
        if age is not None:
            updates["age"] = age

        income = cls._extract_income(lowered)
        if income is not None:
            updates["income"] = income

        if re.search(r"\bsc\b", lowered):
            updates["category"] = "SC"
        elif re.search(r"\bst\b", lowered):
            updates["category"] = "ST"
        elif re.search(r"\bobc\b", lowered):
            updates["category"] = "OBC"
        elif "minority" in lowered:
            updates["category"] = "Minority"
        elif "general" in lowered:
            updates["category"] = "General"

        if re.search(r"\b(female|woman|girl|mahila|ladki|lady)\b", lowered):
            updates["gender"] = "female"
        elif re.search(r"\b(male|man|boy|aadmi|purush|gentleman)\b", lowered):
            updates["gender"] = "male"
        elif re.search(r"\b(other|transgender|third gender)\b", lowered):
            updates["gender"] = "other"

        for occupation, keywords in cls.OCCUPATION_MAP.items():
            if any(kw in lowered for kw in keywords):
                updates["occupation"] = occupation
                break

        if "bpl" in lowered or "ration card" in lowered:
            updates["has_bpl_card"] = not any(x in lowered for x in ["no bpl", "without bpl", "bpl nahi"])

        if any(x in lowered for x in ["marginal", "small farmer", "chhoti zameen", "thoda khet"]):
            updates["farmer_type"] = "marginal"
        elif any(x in lowered for x in ["small", "medium farmer"]):
            updates["farmer_type"] = "small"
        elif any(x in lowered for x in ["large farmer", "badi zameen", "big farmer"]):
            updates["farmer_type"] = "large"

        if any(x in lowered for x in ["homeless", "ghar nahi", "without house"]):
            updates["housing_status"] = "homeless"
        elif any(x in lowered for x in ["kutcha", "kachcha"]):
            updates["housing_status"] = "kutcha_house"
        elif "pucca" in lowered:
            updates["housing_status"] = "pucca_house"
        elif "rented" in lowered or "kiraye" in lowered:
            updates["housing_status"] = "rented"

        return updates

    def _is_personalization_query(self, message: str, extracted_updates: Dict[str, Any]) -> bool:
        lowered = message.lower()
        if extracted_updates:
            return True
        return any(hint in lowered for hint in self.PERSONALIZATION_HINTS)

    def _match_personalized_schemes(self, profile, query: str) -> Dict[str, List[Dict[str, Any]]]:
        retrieved = rag_engine.retrieve(query, top_k=16)
        confirmed: List[Dict[str, Any]] = []
        probable: List[Dict[str, Any]] = []
        seen = set()

        for scheme, score in retrieved:
            if scheme.scheme_id in seen:
                continue
            seen.add(scheme.scheme_id)

            is_eligible, rule_results = eligibility_engine.check_eligibility(profile, scheme)
            failed = [r.reason for r in rule_results if r.status == "fail"]
            missing = [r.rule for r in rule_results if r.status == "missing"]

            if failed:
                continue

            item = {
                "scheme": scheme,
                "score": score,
                "missing": missing,
            }

            if is_eligible and not missing:
                confirmed.append(item)
            elif is_eligible and len(missing) <= 2:
                probable.append(item)

        confirmed.sort(key=lambda x: x["score"], reverse=True)
        probable.sort(key=lambda x: x["score"], reverse=True)

        return {
            "confirmed": confirmed[:3],
            "probable": probable[:2],
        }

    def _build_personalization_block(self, profile, matches: Dict[str, List[Dict[str, Any]]], missing_questions: List[str]) -> str:
        confirmed = matches.get("confirmed", [])
        probable = matches.get("probable", [])

        lines = [
            "=== PERSONALIZATION MODE ===",
            f"PROFILE SNAPSHOT: age={profile.age}, income={profile.income}, category={profile.category}, gender={profile.gender}, occupation={profile.occupation}, bpl={profile.has_bpl_card}",
        ]

        if confirmed:
            lines.append("DIRECTLY ELIGIBLE SCHEMES (use these first):")
            for i, item in enumerate(confirmed, 1):
                scheme = item["scheme"]
                benefits = scheme.benefits
                docs = ", ".join(d.get("name", "") for d in scheme.documents_required[:4]) or "Aadhaar"
                app = scheme.application_process or {}
                how = app.get("online_url") or "Visit local block office"
                lines.append(
                    f"{i}. [[{scheme.name} ({scheme.name_hindi}) →]]({scheme.scheme_id}) | Benefit: {benefits.get('description', 'N/A')} | Docs: {docs} | Apply: {how}"
                )

        if probable:
            lines.append("MAY ALSO APPLY (need one or two more details):")
            for i, item in enumerate(probable, 1):
                scheme = item["scheme"]
                missing = ", ".join(item["missing"])
                lines.append(
                    f"{i}. [[{scheme.name} ({scheme.name_hindi}) →]]({scheme.scheme_id}) | Missing to confirm: {missing}"
                )

        if missing_questions:
            lines.append(f"ASK NEXT (exactly one): {missing_questions[0]}")

        if not confirmed and not probable:
            lines.append("NO CONFIRMED MATCHES YET for current profile details.")

        lines.append("=== END PERSONALIZATION MODE ===")
        return "\n".join(lines)

    def _run_deterministic_verification(self, profile, retrieved_schemes: List[Tuple[Any, float]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Verify retrieved schemes using hard-rule eligibility engine.

        Allowed schemes: all evaluated rules are only pass/missing (no fail).
        Rejected schemes: at least one fail rule.
        """
        allowed: List[Dict[str, Any]] = []
        rejected: List[Dict[str, Any]] = []
        seen = set()

        for scheme, score in retrieved_schemes:
            if scheme.scheme_id in seen:
                continue
            seen.add(scheme.scheme_id)

            is_eligible, rule_results = eligibility_engine.check_eligibility(profile, scheme)
            failed_rules = [r.reason for r in rule_results if r.status == "fail"]
            missing_rules = [r.rule for r in rule_results if r.status == "missing"]
            passed_rules = [r.rule for r in rule_results if r.status == "pass"]

            item = {
                "scheme": scheme,
                "score": score,
                "is_eligible": is_eligible,
                "failed_rules": failed_rules,
                "missing_rules": missing_rules,
                "passed_rules": passed_rules,
            }

            if failed_rules:
                rejected.append(item)
            else:
                allowed.append(item)

        allowed.sort(key=lambda x: x["score"], reverse=True)
        rejected.sort(key=lambda x: x["score"], reverse=True)
        return allowed, rejected

    def _build_verified_context(self, allowed_items: List[Dict[str, Any]]) -> str:
        """Build LLM context using only deterministically allowed schemes."""
        if not allowed_items:
            return "NO VERIFIED SCHEMES AVAILABLE AFTER DETERMINISTIC ELIGIBILITY CHECK."

        context_parts = [f"=== VERIFIED SCHEME KNOWLEDGE (Top {len(allowed_items)} deterministic matches) ===\n"]

        for i, item in enumerate(allowed_items, 1):
            scheme = item["scheme"]
            benefits = scheme.benefits
            hard = scheme.eligibility.get("hard_constraints", {})
            docs = [d.get("name", "") for d in scheme.documents_required[:5]]
            app = scheme.application_process or {}
            app_info = app.get("online_url") or "Contact local government office"
            missing = item.get("missing_rules", [])

            elig_parts = []
            if hard.get("min_age") is not None:
                elig_parts.append(f"Min Age: {hard['min_age']}")
            if hard.get("max_age") is not None:
                elig_parts.append(f"Max Age: {hard['max_age']}")
            if hard.get("max_income_annual") is not None:
                elig_parts.append(f"Max Income: ₹{hard['max_income_annual']:,}/year")
            if hard.get("categories"):
                elig_parts.append(f"Categories: {', '.join(hard['categories'])}")
            if hard.get("gender"):
                elig_parts.append(f"Gender: {', '.join(hard['gender'])}")
            if hard.get("occupation"):
                elig_parts.append(f"Occupation: {', '.join(hard['occupation'])}")

            status_line = "PASS"
            if missing:
                status_line = f"MISSING DATA ({', '.join(missing)})"

            context_parts.append(f"""--- VERIFIED SCHEME {i}: {scheme.name} ({scheme.name_hindi}) ---
LINK_ID: {scheme.scheme_id}
DETERMINISTIC_STATUS: {status_line}
Department: {scheme.department}
Description: {scheme.description}

ELIGIBILITY:
{chr(10).join('  • ' + e for e in elig_parts) if elig_parts else '  No specific hard constraints.'}

BENEFITS:
  Type: {benefits.get('type', 'N/A')}
  Amount: {'₹' + str(benefits['amount']) if benefits.get('amount') else 'Varies'}
  Frequency: {benefits.get('frequency', 'N/A')}
  Details: {benefits.get('description', 'N/A')}

DOCUMENTS NEEDED:
  {', '.join(docs) if docs else 'N/A'}

HOW TO APPLY:
  {app_info}
""")

        context_parts.append("=== END VERIFIED SCHEME KNOWLEDGE ===")
        return "\n".join(context_parts)

    def _build_deterministic_guard_block(self, allowed_items: List[Dict[str, Any]], rejected_items: List[Dict[str, Any]]) -> str:
        """Authoritative guardrail block for the LLM about what can/cannot be recommended."""
        lines = ["=== DETERMINISTIC VERIFICATION (AUTHORITATIVE) ==="]

        if allowed_items:
            lines.append("ALLOWED_FOR_RECOMMENDATION (only these LINK_IDs):")
            for item in allowed_items[:8]:
                scheme = item["scheme"]
                status = "pass" if not item.get("missing_rules") else "missing"
                lines.append(f"- {scheme.scheme_id} | {scheme.name} | status={status}")
        else:
            lines.append("ALLOWED_FOR_RECOMMENDATION: none")

        if rejected_items:
            lines.append("REJECTED_BY_HARD_RULES (do not recommend):")
            for item in rejected_items[:8]:
                scheme = item["scheme"]
                reason = "; ".join(item.get("failed_rules", [])[:2]) or "hard constraint failed"
                lines.append(f"- {scheme.scheme_id} | {scheme.name} | reason={reason}")

        lines.append("STRICT RULE: Recommend/list ONLY ALLOWED_FOR_RECOMMENDATION schemes. Never recommend rejected schemes.")
        lines.append("=== END DETERMINISTIC VERIFICATION ===")
        return "\n".join(lines)

    async def _prepare_generation_payload(self, session_id: str, message: str) -> Dict[str, Any]:
        chat_history = await db_client.get_chat_history(session_id, limit=8)
        profile = await db_client.get_profile(session_id)

        extracted_updates = self._extract_profile_updates(message)
        if extracted_updates:
            profile = profile_manager.update_profile(profile, extracted_updates)
            await db_client.save_profile(profile)

        # Multi-agent connection: retrieve -> deterministic rule verification -> LLM generation.
        retrieved_candidates = rag_engine.retrieve(message, top_k=12)
        allowed_items, rejected_items = self._run_deterministic_verification(profile, retrieved_candidates)
        rag_context = self._build_verified_context(allowed_items[:6])
        deterministic_guard_block = self._build_deterministic_guard_block(allowed_items, rejected_items)

        history_text = ""
        if chat_history:
            for h in chat_history[-4:]:
                role_label = "User" if h["role"] == "user" else "Samarth"
                history_text += f"{role_label}: {h['content']}\n"

        personalization_mode = self._is_personalization_query(message, extracted_updates)
        missing_questions = [m.question for m in profile_manager.get_missing_fields(profile, max_questions=1)]

        matches = {"confirmed": [], "probable": []}
        personalization_block = ""
        if personalization_mode:
            matches = self._match_personalized_schemes(profile, message)
            personalization_block = self._build_personalization_block(profile, matches, missing_questions)

        generation_prompt = f"""CONVERSATION HISTORY:
{history_text if history_text else "(First message in conversation)"}

USER'S LATEST QUESTION: "{message}"

{rag_context}

    {deterministic_guard_block}

{personalization_block if personalization_block else ""}

IMPORTANT INSTRUCTIONS:
1. Always respond like Samarth, a warm Jharkhand officer in natural Hinglish.
2. If PERSONALIZATION MODE is active, prioritize the DIRECTLY ELIGIBLE SCHEMES list for recommendations.
    3. Recommend/list schemes ONLY from ALLOWED_FOR_RECOMMENDATION in deterministic verification.
    4. For recommendations, use this exact clickable format: [[Scheme Name →]](scheme_id).
4. Keep scheme output beautifully formatted with numbered list + bullets for Benefit, Eligibility, Documents, How to apply.
5. If profile details are incomplete, ask exactly ONE next most important question.
6. If user asks about one suggested scheme, give full detail for that scheme.
7. Never show technical/internal phrases like retrieved knowledge, relevance tag, score, ID field labels.
8. Keep tone human, helpful, and concise."""

        source_items = matches.get("confirmed", []) + matches.get("probable", [])
        if source_items:
            sources = [
                {
                    "scheme_id": item["scheme"].scheme_id,
                    "scheme_name": item["scheme"].name,
                    "scheme_name_hindi": item["scheme"].name_hindi,
                    "category": item["scheme"].category,
                    "relevance_score": round(item["score"], 2),
                }
                for item in source_items
            ]
        else:
            verified_for_sources = [(item["scheme"], item["score"]) for item in allowed_items]
            sources = self._build_sources(verified_for_sources)

        return {
            "generation_prompt": generation_prompt,
            "chat_history": chat_history,
            "sources": sources,
        }

    @staticmethod
    def _build_sources(retrieved_schemes: List) -> List[Dict[str, Any]]:
        """Filter retrieval results into frontend source cards with safe low-score fallback."""
        if not retrieved_schemes:
            return []

        max_score = max(score for _, score in retrieved_schemes)
        min_threshold = max(0.15, max_score * 0.3)

        filtered = [(scheme, score) for scheme, score in retrieved_schemes if score >= min_threshold]
        if not filtered and retrieved_schemes:
            filtered = [retrieved_schemes[0]]

        sources = []
        for scheme, score in filtered:
            sources.append({
                "scheme_id": scheme.scheme_id,
                "scheme_name": scheme.name,
                "scheme_name_hindi": scheme.name_hindi,
                "category": scheme.category,
                "relevance_score": round(score, 2),
            })
        return sources

    async def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process a user message using RAG pipeline."""
        payload = await self._prepare_generation_payload(session_id, message)

        # 4. Generate response
        response_text = await llm_client.generate_response(
            prompt=payload["generation_prompt"],
            history=[{"role": "user", "content": RAG_SYSTEM_PROMPT}]
        )
        sources = payload["sources"]

        # 6. Save to DB
        await db_client.add_message(session_id, "user", message)
        await db_client.add_message(session_id, "assistant", response_text)

        return {
            "session_id": session_id,
            "response": response_text,
            "sources": sources,
            "metadata": {
                "total_retrieved": len(sources),
                "rag_mode": True,
            }
        }

    async def process_message_stream(self, session_id: str, message: str):
        """Process a user message using RAG pipeline, streaming the response."""
        payload = await self._prepare_generation_payload(session_id, message)
        sources = payload["sources"]

        # Yield sources first
        yield json.dumps({"type": "sources", "sources": sources}) + "\n"

        # 5. Stream response
        response_text = ""
        async for chunk in llm_client.generate_response_stream(
            prompt=payload["generation_prompt"],
            history=[{"role": "user", "content": RAG_SYSTEM_PROMPT}]
        ):
            response_text += chunk
            yield json.dumps({"type": "chunk", "text": chunk}) + "\n"

        # 6. Save to DB afterwards
        await db_client.add_message(session_id, "user", message)
        await db_client.add_message(session_id, "assistant", response_text)
        
        yield json.dumps({"type": "done"}) + "\n"


pure_ai_assistant = PureAIAssistant()
