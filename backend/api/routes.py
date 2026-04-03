from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from backend.api.models import ChatRequest, ChatResponse, ProfileUpdateRequest, WhatIfRequest, WhatIfResponse, AIAssistantRequest, AIAssistantResponse
from backend.core.orchestrator import orchestrator
from backend.core.pure_ai_assistant import pure_ai_assistant
from backend.db.database import db_client
from backend.data.loader import scheme_db
from backend.core.what_if import what_if_simulator
from backend.db.models import Scheme, UserProfile

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Main communication endpoint. Takes user message, extracts intent, 
    calculates eligibility, and returns LLM response.
    """
    try:
        result = await orchestrator.process_message(request.session_id, request.message)
        return ChatResponse(**result)
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Error in chat endpoint: {e}")
        
        if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="Gemini API ka quota khatam ho gaya hai. Thodi der baad try karein (1-2 minute). Free tier mein limited requests hain."
            )
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/categories")
async def get_categories():
    """Returns unique categories with counts."""
    schemes = scheme_db.get_all_schemes()
    cat_counts = {}
    for s in schemes:
        cat_counts[s.category] = cat_counts.get(s.category, 0) + 1
        
    return [{"id": k, "count": v, "name": k.replace("_", " ").title()} for k, v in cat_counts.items()]

@router.get("/schemes", response_model=List[Scheme])
async def list_schemes(category: str = None):
    """Returns all schemes, optionally filtered by category."""
    schemes = scheme_db.get_all_schemes()
    if category:
        schemes = [s for s in schemes if s.category.lower() == category.lower()]
    return schemes

@router.get("/schemes/{scheme_id}", response_model=Scheme)
async def get_scheme(scheme_id: str):
    """Get scheme details by ID."""
    scheme = scheme_db.get_scheme_by_id(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme

@router.get("/profile/{session_id}", response_model=UserProfile)
async def get_profile(session_id: str):
    """Returns the current accumulated profile for a user session."""
    profile = await db_client.get_profile(session_id)
    return profile

@router.post("/profile/{session_id}")
async def update_profile(session_id: str, request: ProfileUpdateRequest):
    """Directly update profile fields (for UI forms)."""
    profile = await db_client.get_profile(session_id)
    # Convert dict to only include keys that are fields in UserProfile model
    valid_keys = UserProfile.model_fields.keys()
    update_data = {k:v for k,v in request.model_dump().items() if k in valid_keys and v is not None}
    
    if update_data:
         updated_profile = profile.model_copy(update=update_data)
         await db_client.save_profile(updated_profile)
    return {"status": "success"}

@router.post("/whatif", response_model=WhatIfResponse)
async def whatif_simulation(request: WhatIfRequest):
    """Run a scenario simulation on the user's profile."""
    profile = await db_client.get_profile(request.session_id)
    results = what_if_simulator.run_simulation(profile, request.overrides)
    
    formatted = []
    for r in results:
         formatted.append({
             "scheme_id": r.scheme_id,
             "eligible": r.eligible,
             "score": r.score,
             "failed_rules": r.failed_rules,
             "missing_data": r.missing_data
         })
         
    return WhatIfResponse(simulated_results=formatted)

@router.delete("/session/{session_id}")
async def reset_session(session_id: str):
    """Reset a session: clear profile and chat history."""
    await db_client.reset_session(session_id)
    return {"status": "success", "message": "Session reset"}

@router.post("/ai-chat", response_model=AIAssistantResponse)
async def ai_assistant_endpoint(request: AIAssistantRequest):
    """
    Pure AI Assistant endpoint powered by RAG.
    Retrieves relevant scheme data and uses LLM to answer comprehensively.
    """
    try:
        result = await pure_ai_assistant.process_message(request.session_id, request.message)
        return AIAssistantResponse(**result)
    except Exception as e:
        error_msg = str(e).lower()
        print(f"Error in AI assistant endpoint: {e}")
        
        if "429" in str(e) or "quota" in error_msg or "rate" in error_msg:
            raise HTTPException(
                status_code=429, 
                detail="API rate limit reached. Please wait a moment and try again."
            )
        raise HTTPException(status_code=500, detail=str(e))
