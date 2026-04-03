from pydantic import BaseModel, ConfigDict
from typing import Dict, Any, List, Optional
from backend.db.models import UserProfile, Scheme

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: Optional[str] = "en"

class ChatResponse(BaseModel):
    session_id: str
    response: str
    profile_snapshot: Dict[str, Any]
    schemes_evaluated: List[Dict[str, Any]]
    metadata: Dict[str, Any]

class ProfileUpdateRequest(BaseModel):
    # Dynamic update of profile fields
    model_config = ConfigDict(extra='allow')
    
class WhatIfRequest(BaseModel):
    session_id: str
    overrides: Dict[str, Any]
    
class WhatIfResponse(BaseModel):
    simulated_results: List[Dict[str, Any]]

class AIAssistantRequest(BaseModel):
    session_id: str
    message: str

class AIAssistantResponse(BaseModel):
    session_id: str
    response: str
    sources: List[Dict[str, Any]]
    metadata: Dict[str, Any]
