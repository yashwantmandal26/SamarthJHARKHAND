from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from backend.api.models import ChatRequest, ChatResponse, ProfileUpdateRequest, WhatIfRequest, WhatIfResponse
from backend.core.orchestrator import orchestrator
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
        print(f"Error in chat endpoint: {e}")
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
