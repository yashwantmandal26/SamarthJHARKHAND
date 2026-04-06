from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class Scheme(BaseModel):
    model_config = ConfigDict(extra='ignore')

    scheme_id: str
    name: str
    name_hindi: str
    department: str
    category: str
    description: str
    eligibility: Dict[str, Any]
    benefits: Dict[str, Any]
    documents_required: List[Dict[str, Any]]
    application_process: Dict[str, Any]
    tags: List[str]


class UserProfile(BaseModel):
    session_id: str
    name: Optional[str] = None
    age: Optional[int] = None
    income: Optional[int] = None
    category: Optional[str] = None       # SC / ST / OBC / General / Minority
    gender: Optional[str] = None
    occupation: Optional[str] = None     # farmer / student / artisan / labourer / unemployed / self_employed
    farmer_type: Optional[str] = None    # marginal / small / large
    housing_status: Optional[str] = None # homeless / kutcha_house / pucca_house / rented / slum
    student_class: Optional[int] = None  # 1-12 for grades, 15 for UG (Bachelors), 17 for PG (Masters)
    district: Optional[str] = None
    education: Optional[str] = None
    marital_status: Optional[str] = None # married / unmarried / widow / divorced
    disabilities: List[str] = []
    has_bpl_card: Optional[bool] = None
    scheme_interest: Optional[str] = None  # user-stated interest area


class ConversationMessage(BaseModel):
    role: str       # user, assistant, system
    content: str
    timestamp: str


class EligibilityResult(BaseModel):
    scheme_id: str
    scheme_name: str = ""
    eligible: bool
    score: float
    passed_rules: List[str]
    failed_rules: List[str]
    missing_data: List[str]
    explanation: Optional[str] = None
