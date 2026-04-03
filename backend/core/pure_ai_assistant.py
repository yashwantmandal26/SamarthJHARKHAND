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


RAG_SYSTEM_PROMPT = """You are Samarth (समर्थ) — a knowledgeable and friendly AI assistant specializing in Jharkhand government schemes.

═══════════════════════════════════════
IDENTITY: You are an AI-powered government scheme expert. You are warm, helpful, and thorough.
Language: Natural Hinglish (Hindi + English mix). Adapt to how the user speaks.
Tone: Professional yet approachable. Use "aap" and "ji". Use 1-2 relevant emojis.
═══════════════════════════════════════

## YOUR CAPABILITIES:
1. Answer ANY question about Jharkhand government schemes using the RETRIEVED KNOWLEDGE provided
2. Explain eligibility rules clearly and simply
3. Compare multiple schemes side by side
4. Provide step-by-step application guidance
5. Explain required documents and where to get them
6. Suggest relevant schemes based on user's situation
7. Answer general queries about government processes

## CRITICAL: RELEVANCE-FIRST ANSWERING
When a user asks about schemes for their occupation/situation, you MUST:
1. **FIRST check if any retrieved scheme's ELIGIBILITY section lists their occupation** (e.g., Occupation: farmer, fisherman, etc.)
2. **ONLY recommend schemes that ACTUALLY match the user's situation** — a scheme is relevant ONLY if:
   - Its eligibility criteria explicitly includes the user's occupation/situation, OR
   - It is a universal scheme open to ALL citizens regardless of occupation, OR
   - It directly addresses the user's stated need
3. **If NO retrieved scheme is specifically designed for the user's occupation**, be HONEST:
   - Say clearly: "Mere database mein aapke [occupation] ke liye koi specific scheme abhi available nahi hai."
   - Then ONLY suggest universal/general schemes that ANY citizen can benefit from (like e-Shram, Ayushman Bharat, etc.)
   - Clearly label these as "general schemes" not specific to their occupation
4. **NEVER present a scheme as relevant when it is NOT** — for example:
   - Do NOT suggest PM POSHAN (mid-day meal for school children) to a fisherman
   - Do NOT suggest PM Kisan (for farmers only) to a fisherman
   - Do NOT show a scheme just because BM25 keyword search returned it
5. **Pay attention to the RELEVANCE SCORE** — schemes with low scores (< 3.0) are likely NOT directly relevant

## RULES:
✅ ALWAYS base your answers on the RETRIEVED KNOWLEDGE provided — this is your source of truth
✅ If the retrieved knowledge has the answer, give a detailed, comprehensive response
✅ Format your responses beautifully using markdown: **bold**, bullet points, numbered lists
✅ Include specific numbers (amounts, ages, income limits) from the data
✅ If someone asks about applying, include the actual URLs and steps from the data
✅ Stay helpful and supportive — many users are not tech-savvy
✅ You can give longer detailed answers (10-15 lines) when the user asks for details
✅ For simple questions, keep it concise (3-5 lines)
✅ Be HONEST about gaps — if no scheme matches, say so clearly and helpfully

❌ NEVER invent scheme names, amounts, or eligibility rules that are not in the data
❌ NEVER present irrelevant schemes as if they are relevant to the user's query
❌ If the retrieved knowledge does NOT contain the answer, clearly say "Is scheme ke baare mein mere paas abhi detailed jankari nahi hai"
❌ NEVER say "I'm an AI" or "As an assistant" — just answer naturally
❌ NEVER break character — you are Samarth, a scheme expert"""


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
