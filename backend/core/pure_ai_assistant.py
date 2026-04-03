"""
Pure AI Assistant — RAG-powered conversational assistant.

Unlike the eligibility-matching orchestrator, this uses pure LLM + RAG
to answer ANY question about government schemes comprehensively.
"""

import json
from typing import Dict, Any, List
from backend.db.database import db_client
from backend.core.rag_engine import rag_engine
from backend.llm.client import llm_client


RAG_SYSTEM_PROMPT = """You are **Samarth (समर्थ)** — a senior government scheme advisor from Jharkhand. You speak like a real, experienced government officer sitting across the desk from a citizen, helping them personally.

## YOUR IDENTITY
- You are a **human officer**, NOT an AI. Never say "I'm an AI" or "As a language model."
- Your name is **Samarth** — a trusted advisor at the Jharkhand Government Help Desk.
- You speak in **warm, natural Hinglish** (Hindi + English mix). Adapt to the user's language.
- Use **"aap"** and **"ji"** respectfully. Use 1-2 relevant emojis per response (not more).
- Be warm but **professional** — like a helpful senior officer who genuinely cares.

## RESPONSE FORMAT (MANDATORY)
You MUST format every response using clean, structured markdown:

1. **Start with a warm greeting line** — address the user's query directly (1 line max)
2. **Use numbered sections** with bold headings for each scheme or topic:
   - `**1. Scheme Name (हिंदी नाम)**`
   - Under each, use bullet points for details
3. **Use bold** for important information: amounts (₹), deadlines, eligibility criteria
4. **Use bullet points** (`-` or `•`) for listing documents, steps, benefits
5. **End with a helpful closing** — offer to explain more or suggest next steps

### EXAMPLE FORMAT:
```
Namaste ji! 🙏 Aapke sawaal ka jawab deta hoon:

**1. PM Kisan Samman Nidhi (पीएम किसान सम्मान निधि)**
- **Benefit:** ₹6,000 per year (3 installments of ₹2,000)
- **Eligibility:** Small/marginal farmers with cultivable land
- **Documents needed:**
  - Aadhaar Card
  - Bank Account (with IFSC)
  - Land ownership documents
- **How to apply:** Visit pmkisan.gov.in → New Farmer Registration

**2. Kisan Credit Card (किसान क्रेडिट कार्ड)**
- **Benefit:** Low-interest crop loans up to ₹3 lakh at 4% interest
- **Eligibility:** All farmers (including tenant farmers)

Aapko kisi scheme ke baare mein aur detail chahiye toh zaroor poochiye! 😊
```

## CRITICAL RULES FOR RELEVANCE
- **ONLY recommend schemes that ACTUALLY match** the user's occupation/situation
- If a scheme's eligibility says "farmer" but user is "fisherman" — it is NOT relevant for general recs
- **EXCEPTION:** If user asks about a **specific scheme by name**, ALWAYS answer with full details, but politely mention eligibility constraints
- If NO scheme matches, be honest: "Aapke liye specific scheme mere database mein nahi mil raha"
- **NEVER invent** scheme names, amounts, or rules not present in the retrieved data
- **NEVER dump all retrieved schemes** — only show what's truly relevant

## TONE GUIDELINES
- Be **specific** — always include exact amounts, percentages, age limits from the data
- Be **actionable** — give URLs, office names, steps the user can actually follow
- Be **honest** — if you're unsure or data is missing, say so clearly
- Keep responses **medium length** (8-15 lines) for detailed queries, **short** (3-5 lines) for simple ones
- Sound like a **knowledgeable human**, not a database dump"""


class PureAIAssistant:
    """RAG-powered AI assistant for comprehensive scheme information."""

    async def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Process a user message using RAG pipeline."""

        # 1. Get chat history for context
        chat_history = await db_client.get_chat_history(session_id, limit=8)

        # 2. Retrieve relevant schemes via RAG
        rag_context = rag_engine.build_context(
            query=message,
            chat_history=chat_history,
            top_k=4  # Reduced from 8 to 4 to drastically speed up local LLM response time
        )

        # 3. Build the prompt with retrieved context
        history_text = ""
        if chat_history:
            for h in chat_history[-4:]:
                role_label = "User" if h["role"] == "user" else "Samarth"
                history_text += f"{role_label}: {h['content']}\n"

        generation_prompt = f"""CONVERSATION HISTORY:
{history_text if history_text else "(First message in conversation)"}

USER'S LATEST QUESTION: "{message}"

{rag_context}

IMPORTANT INSTRUCTIONS:
1. Before answering, ANALYZE each retrieved scheme — does it ACTUALLY match the user's question/situation?
2. A scheme is generally RELEVANT only if its eligibility criteria (especially Occupation field) matches the user, OR it's a universal scheme for all citizens.
3. EXCEPTION FOR DIRECT QUESTIONS: If the user explicitly asks about a specific scheme by name (e.g., "How to apply for PM Kisan"), you MUST answer their question using the retrieved data. Even if it is marked as NOT RELEVANT to their occupation, you MUST provide the requested details (like application steps) but politely mention they might not be eligible. Do NOT refuse to answer direct questions.
4. If a scheme's eligibility says "Occupation: farmer" but the user is a fisherman, that scheme is NOT relevant for general recommendations.
5. If the user asks for general recommendations ("What schemes are for me?") and NONE of the retrieved schemes are directly relevant, clearly say so.
6. You may mention universal/general welfare schemes but clearly label them as "general schemes available to all citizens" not specific to their situation.
7. DO NOT just list all retrieved schemes — filter out the irrelevant ones unless the user specifically asked for them.
8. Be honest and natural — saying "no specific scheme found" is better than misleading the user with irrelevant schemes."""

        # 4. Generate response
        response_text = await llm_client.generate_response(
            prompt=generation_prompt,
            history=[{"role": "user", "content": RAG_SYSTEM_PROMPT}]
        )

        # 5. Get the retrieved scheme names for the frontend (with relevance threshold)
        retrieved_schemes = rag_engine.retrieve(message, top_k=8)
        sources = []
        # Only include schemes with meaningful relevance scores
        # This prevents noise low-scoring schemes from showing up
        if retrieved_schemes:
            max_score = max(score for _, score in retrieved_schemes) if retrieved_schemes else 0
            # Dynamic threshold: at least 30% of max score to be considered relevant
            min_threshold = max(1.0, max_score * 0.3)
            for scheme, score in retrieved_schemes:
                if score >= min_threshold:
                    sources.append({
                        "scheme_id": scheme.scheme_id,
                        "scheme_name": scheme.name,
                        "scheme_name_hindi": scheme.name_hindi,
                        "category": scheme.category,
                        "relevance_score": round(score, 2),
                    })

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
        # 1. Get chat history for context
        chat_history = await db_client.get_chat_history(session_id, limit=8)

        # 2. Retrieve relevant schemes via RAG
        rag_context = rag_engine.build_context(
            query=message,
            chat_history=chat_history,
            top_k=4
        )

        # 3. Build the prompt
        history_text = ""
        if chat_history:
            for h in chat_history[-4:]:
                role_label = "User" if h["role"] == "user" else "Samarth"
                history_text += f"{role_label}: {h['content']}\n"

        generation_prompt = f"""CONVERSATION HISTORY:
{history_text if history_text else "(First message in conversation)"}

USER'S LATEST QUESTION: "{message}"

{rag_context}

IMPORTANT INSTRUCTIONS:
1. Before answering, ANALYZE each retrieved scheme — does it ACTUALLY match the user's question/situation?
2. A scheme is generally RELEVANT only if its eligibility criteria (especially Occupation field) matches the user, OR it's a universal scheme for all citizens.
3. EXCEPTION FOR DIRECT QUESTIONS: If the user explicitly asks about a specific scheme by name (e.g., "How to apply for PM Kisan"), you MUST answer their question using the retrieved data. Even if it is marked as NOT RELEVANT to their occupation, you MUST provide the requested details (like application steps) but politely mention they might not be eligible. Do NOT refuse to answer direct questions.
4. If a scheme's eligibility says "Occupation: farmer" but the user is a fisherman, that scheme is NOT relevant for general recommendations.
5. If the user asks for general recommendations ("What schemes are for me?") and NONE of the retrieved schemes are directly relevant, clearly say so.
6. You may mention universal/general welfare schemes but clearly label them as "general schemes available to all citizens" not specific to their situation.
7. DO NOT just list all retrieved schemes — filter out the irrelevant ones unless the user specifically asked for them.
8. Be honest and natural — saying "no specific scheme found" is better than misleading the user with irrelevant schemes."""

        # 4. Get the retrieved scheme names for the frontend
        retrieved_schemes = rag_engine.retrieve(message, top_k=8)
        sources = []
        if retrieved_schemes:
            max_score = max(score for _, score in retrieved_schemes) if retrieved_schemes else 0
            min_threshold = max(1.0, max_score * 0.3)
            for scheme, score in retrieved_schemes:
                if score >= min_threshold:
                    sources.append({
                        "scheme_id": scheme.scheme_id,
                        "scheme_name": scheme.name,
                        "scheme_name_hindi": scheme.name_hindi,
                        "category": scheme.category,
                        "relevance_score": round(score, 2),
                    })

        # Yield sources first
        yield json.dumps({"type": "sources", "sources": sources}) + "\n"

        # 5. Stream response
        response_text = ""
        async for chunk in llm_client.generate_response_stream(
            prompt=generation_prompt,
            history=[{"role": "user", "content": RAG_SYSTEM_PROMPT}]
        ):
            response_text += chunk
            yield json.dumps({"type": "chunk", "text": chunk}) + "\n"

        # 6. Save to DB afterwards
        await db_client.add_message(session_id, "user", message)
        await db_client.add_message(session_id, "assistant", response_text)
        
        yield json.dumps({"type": "done"}) + "\n"


pure_ai_assistant = PureAIAssistant()
