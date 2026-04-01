from typing import List, Dict, Any
from pydantic import BaseModel
from backend.db.models import Scheme, UserProfile

class DocumentCheck(BaseModel):
    document_id: str
    name: str
    is_mandatory: bool
    status: str # "provided", "missing", "unknown"
    advice: str

class DocumentGuidance:
    """Evaluates which documents user has vs what's required."""

    def check_requirements(self, scheme: Scheme, user_docs_owned: List[str]) -> List[DocumentCheck]:
        results = []
        for doc in scheme.documents_required:
            is_mandatory = doc.get("mandatory", False)
            doc_id = doc.get("id")
            name = doc.get("name")
            
            status = "unknown"
            if doc_id in user_docs_owned:
                status = "provided"
            else:
                status = "missing"
                
            advice = f"You need to provide your {name}." if is_mandatory else f"Providing your {name} is optional but recommended."
            if status == "provided":
                advice = "Already provided."
                
            results.append(DocumentCheck(
                document_id=doc_id,
                name=name,
                is_mandatory=is_mandatory,
                status=status,
                advice=advice
            ))
        return results

document_guidance = DocumentGuidance()
