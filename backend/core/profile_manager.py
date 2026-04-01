from typing import Dict, Any, List
from pydantic import BaseModel
from backend.db.models import UserProfile

class MissingField(BaseModel):
    field: str
    description: str
    question: str

class ProfileManager:
    """Manages merging new profile data and identifying missing required fields."""
    
    # Base fields that are always good to have
    CORE_FIELDS = ['age', 'income', 'category', 'gender']

    def update_profile(self, current_profile: UserProfile, new_data: Dict[str, Any]) -> UserProfile:
        """Merges new extracted data into the profile and updates DB."""
        # Filter out Nones and empty strings from new_data
        valid_updates = {k: v for k, v in new_data.items() if v is not None and v != ""}
        
        # Merge lists (like disabilities)
        if 'disabilities' in valid_updates and isinstance(valid_updates['disabilities'], list):
            existing = set(current_profile.disabilities)
            existing.update(valid_updates['disabilities'])
            valid_updates['disabilities'] = list(existing)

        # Update the pydantic model directly
        updated_profile = current_profile.model_copy(update=valid_updates)
        return updated_profile

    def get_missing_fields(self, profile: UserProfile) -> List[MissingField]:
        """Checks which core fields are missing from the profile based on what is known."""
        missing = []
        
        # If we know their general context, we can ask targeted questions. For general case:
        if profile.age is None:
            missing.append(MissingField(
                field="age",
                description="Age",
                question="Could you please tell me your age?"
            ))
        
        # In a real system, we'd only ask these if relevant to their scheme_interest,
        # but for MVP we will try to complete the profile progressively.
        if profile.gender is None and len(missing) < 2:
            missing.append(MissingField(
                field="gender",
                description="Gender",
                question="What is your gender?"
            ))
            
        if profile.category is None and len(missing) < 2:
            missing.append(MissingField(
                field="category",
                description="Social Category",
                question="Do you belong to General, SC, ST, or OBC category?"
            ))
            
        if profile.income is None and len(missing) < 2:
            missing.append(MissingField(
                field="income",
                description="Annual Income",
                question="What is your approximate annual family income?"
            ))
            
        if profile.occupation is None and len(missing) < 2:
             missing.append(MissingField(
                field="occupation",
                description="Occupation",
                question="What do you do for a living (e.g., student, farmer, self-employed)?"
            ))

        return missing

profile_manager = ProfileManager()
