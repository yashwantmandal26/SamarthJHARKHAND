from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from backend.db.models import UserProfile


class MissingField(BaseModel):
    field: str
    description: str
    question: str
    priority: int = 5  # 1=highest, 10=lowest


class ProfileManager:
    """Manages merging new profile data and identifying CONTEXTUALLY relevant missing fields."""

    # ── Context-driven question banks ──────────────────────────────
    # These define which fields matter MOST for each interest/occupation
    CONTEXT_PRIORITIES: Dict[str, List[str]] = {
        "agriculture": ["income", "farmer_type", "age", "category", "has_bpl_card"],
        "housing": ["income", "housing_status", "category", "age", "has_bpl_card"],
        "education": ["age", "student_class", "gender", "income", "category"],
        "women": ["age", "gender", "marital_status", "income", "category"],
        "employment": ["age", "gender", "income", "occupation", "category"],
        "social_security": ["age", "income", "marital_status", "category", "has_bpl_card"],
    }

    # Natural Hinglish questions for each field
    FIELD_QUESTIONS: Dict[str, Dict[str, str]] = {
        "age": {
            "description": "Age",
            "question": "Aapki umar kitni hai lagbhag?",
        },
        "income": {
            "description": "Annual Income",
            "question": "Aapki family ki saalana income kitni hogi lagbhag?",
        },
        "gender": {
            "description": "Gender",
            "question": "Ye scheme applicant ladki ke liye hai ya ladke ke liye?",
        },
        "category": {
            "description": "Social Category",
            "question": "Aap kis category mein aate hain — General, SC, ST, ya OBC?",
        },
        "occupation": {
            "description": "Occupation",
            "question": "Aap kya kaam karte hain — farming, naukri, student, ya kuch aur?",
        },
        "farmer_type": {
            "description": "Farm Size",
            "question": "Aapke paas kitni zameen hai? Chhoti (marginal), thodi zyada (small), ya badi?",
        },
        "housing_status": {
            "description": "Housing Situation",
            "question": "Aapka apna ghar hai? Kachcha, pucca, ya kiraye pe?",
        },
        "student_class": {
            "description": "Student Class",
            "question": "Abhi kis class mein padhai chal rahi hai?",
        },
        "marital_status": {
            "description": "Marital Status",
            "question": "Aapki shaadi hui hai ya abhi nahi?",
        },
        "has_bpl_card": {
            "description": "BPL Card",
            "question": "Aapke paas BPL ration card hai kya?",
        },
    }

    def update_profile(self, current_profile: UserProfile, new_data: Dict[str, Any]) -> UserProfile:
        """Merges new extracted data into the profile."""
        valid_updates = {k: v for k, v in new_data.items() if v is not None and v != ""}

        # Merge lists (like disabilities)
        if 'disabilities' in valid_updates and isinstance(valid_updates['disabilities'], list):
            existing = set(current_profile.disabilities or [])
            existing.update(valid_updates['disabilities'])
            valid_updates['disabilities'] = list(existing)

        updated_profile = current_profile.model_copy(update=valid_updates)
        return updated_profile

    def get_missing_fields(self, profile: UserProfile, max_questions: int = 2) -> List[MissingField]:
        """Returns contextually prioritized missing fields based on scheme_interest and occupation."""
        missing = []

        # Determine priority order based on context
        priority_fields = self._get_priority_fields(profile)

        for idx, field in enumerate(priority_fields):
            if len(missing) >= max_questions:
                break

            value = getattr(profile, field, None)
            if value is not None:
                continue

            # Skip irrelevant fields based on context
            if not self._is_field_relevant(field, profile):
                continue

            field_info = self.FIELD_QUESTIONS.get(field)
            if field_info:
                missing.append(MissingField(
                    field=field,
                    description=field_info["description"],
                    question=field_info["question"],
                    priority=idx + 1,
                ))

        return missing

    def _get_priority_fields(self, profile: UserProfile) -> List[str]:
        """Returns fields in priority order based on what we know about the user."""
        # If we know their interest, use that context
        if profile.scheme_interest and profile.scheme_interest in self.CONTEXT_PRIORITIES:
            return self.CONTEXT_PRIORITIES[profile.scheme_interest]

        # If we know their occupation, infer the priority
        if profile.occupation:
            occ = profile.occupation.lower()
            if occ in ("farmer", "fisherman"):
                return self.CONTEXT_PRIORITIES["agriculture"]
            elif occ == "student":
                return self.CONTEXT_PRIORITIES["education"]
            elif occ in ["artisan", "labourer", "self_employed", "unemployed"]:
                return self.CONTEXT_PRIORITIES["employment"]

        # Default: general priority order
        return ["occupation", "income", "age", "category", "gender", "has_bpl_card"]

    def _is_field_relevant(self, field: str, profile: UserProfile) -> bool:
        """Checks if a field is actually relevant to this user's context."""
        # Don't ask farmer_type if they're not a farmer
        if field == "farmer_type" and profile.occupation and profile.occupation.lower() not in ("farmer",):
            return False

        # Don't ask student_class if they're not a student
        if field == "student_class" and profile.occupation and profile.occupation.lower() != "student":
            return False

        # Don't ask housing_status unless related to housing interest
        if field == "housing_status" and profile.scheme_interest and profile.scheme_interest != "housing":
            return False

        return True

    def get_profile_completeness(self, profile: UserProfile) -> Dict[str, Any]:
        """Returns a summary of how complete the profile is for scheme matching."""
        core_fields = ["age", "income", "category", "gender", "occupation"]
        filled = sum(1 for f in core_fields if getattr(profile, f, None) is not None)
        total = len(core_fields)

        return {
            "filled": filled,
            "total": total,
            "percentage": round((filled / total) * 100),
            "has_name": profile.name is not None,
            "has_interest": profile.scheme_interest is not None,
        }


profile_manager = ProfileManager()
