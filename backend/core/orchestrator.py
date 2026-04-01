from typing import Dict, Any, Tuple
import json
from pydantic import BaseModel

from backend.db.database import db_client
from backend.db.models import UserProfile
from backend.core.profile_manager import profile_manager
from backend.core.retrieval import retrieval_engine
from backend.core.scoring import scoring_engine
from backend.llm.client import llm_client
from backend.llm.prompts import Prompts

# Define Schema for JSON Intent Extraction
class IntentExtractionSchema(BaseModel):
    intent: str
    profile_updates: Dict[str, Any]
    query_parameters: Dict[str, Any]

class Orchestrator:
    """The central orchestrator that combines LLM reasoning with code-based deterministic rules."""

    async def process_message(self, session_id: str, message: str) -> Dict[str, Any]:
        """Main flow: Message -> DB -> Profile -> Retrieval -> Eligibility -> LLM Response"""
        
        # 1. Fetch DB State
        profile = await db_client.get_profile(session_id)
        chat_history = await db_client.get_chat_history(session_id, limit=5)
        
        # 2. Extract Intent & Entities (LLM Call 1 - Fast JSON Output)
        extraction_prompt = f"Previous chat context: {chat_history}\n\nUser Message: {message}\n\nExtract the intent, profile updates, and query parameters."
        
        try:
             # We pass the schema directly to Gemini
             raw_extraction = await llm_client.generate_response(
                 prompt=extraction_prompt, 
                 history=[{"role": "user", "content": Prompts.INTENT_EXTRACTION_SYSTEM}],
                 response_schema=IntentExtractionSchema
             )
             
             extraction = json.loads(raw_extraction)
             intent = extraction.get("intent", "general_question")
             profile_updates = extraction.get("profile_updates", {})
             query_params = extraction.get("query_parameters", {})
             
        except Exception as e:
             # Fallback if JSON parsing fails
             print(f"Extraction failed: {e}")
             intent = "general_question"
             profile_updates = {}
             query_params = {}

        # 3. Update Profile (Deterministic Code)
        if profile_updates:
            profile = profile_manager.update_profile(profile, profile_updates)
            await db_client.save_profile(profile)

        # 4. Execute Core Logic based on intent
        system_results = {}
        missing_fields = []
        
        # Always check missing fields
        missing_fields_objs = profile_manager.get_missing_fields(profile)
        missing_fields = [m.field for m in missing_fields_objs]
        
        if intent in ["discover_schemes", "check_eligibility", "general_question"]:
            # Retrieve
            cat_filter = profile.scheme_interest
            
            # If user explicitly states they want to know about agriculture but haven't updated profile yet
            if not cat_filter and "agriculture" in str(query_params).lower():
                cat_filter = "agriculture"
            
            schemes = retrieval_engine.search_schemes(query=query_params.get("scheme_name", ""), category=cat_filter)
            
            # Score & Rank (Deterministic)
            ranked_results = scoring_engine.score_and_rank(profile, schemes)
            
            # Take top 4 for the context
            top_schemes = []
            for r in ranked_results[:4]:
                # If they completely fail hard rules, maybe skip showing it unless it's a specific ask
                if not r.eligible and len(r.passed_rules) == 0 and len(r.missing_data) == 0:
                    continue
                    
                status_text = "Eligible" if r.eligible else "Ineligible (or missing data)"
                top_schemes.append({
                    "scheme_id": r.scheme_id,
                    "scheme_name": r.scheme_name,
                    "status": status_text,
                    "failed_reasons": r.failed_rules,
                    "missing_data": r.missing_data
                })
            
            system_results["top_schemes"] = top_schemes
            
        elif intent == "what_if":
            # Note: A real implementation would parse the 'what_if' parameters from the extraction
            system_results["note"] = "What if simulation requested."
            pass
        
        # 5. Generate Natural Response (LLM Call 2)
        generation_prompt = f"""
        User Message: "{message}"
        Current Intent: {intent}
        
        User Profile Status:
        Name: {profile.name}, Age: {profile.age}, Income: {profile.income}, Category: {profile.category}, Gender: {profile.gender}
        Occupation: {profile.occupation}, Farmer Type: {profile.farmer_type}, Student Class: {profile.student_class}
        Housing: {profile.housing_status}, Marital Status: {profile.marital_status}
        Missing Mandatory Fields we want to collect: {[m.description for m in missing_fields_objs[:2]]}
        
        System Results (DO NOT HALLUCINATE OR CONTRADICT THESE):
        {json.dumps(system_results, indent=2)}
        
        Draft a helpful, human-like response to the user.
        """
        
        response_text = await llm_client.generate_response(
             prompt=generation_prompt,
             history=[{"role": "user", "content": Prompts.RESPONSE_GENERATION_SYSTEM}]
        )
        
        # 6. Save to DB
        await db_client.add_message(session_id, "user", message)
        await db_client.add_message(session_id, "assistant", response_text)
        
        # 7. Format final Output
        return {
            "session_id": session_id,
            "response": response_text,
            "profile_snapshot": profile.model_dump(),
            "schemes_evaluated": system_results.get("top_schemes", []),
            "metadata": {
                "intent": intent,
                "missing_fields": missing_fields
            }
        }

orchestrator = Orchestrator()
