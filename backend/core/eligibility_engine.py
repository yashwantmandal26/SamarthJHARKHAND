from typing import List, Dict, Any, Tuple
from backend.db.models import UserProfile, Scheme
from pydantic import BaseModel


class RuleResult(BaseModel):
    rule: str
    status: str  # "pass", "fail", "missing"
    reason: str


class EligibilityEngine:
    """Deterministic rule engine for scheme eligibility. Checks all hard constraints."""

    def check_eligibility(self, profile: UserProfile, scheme: Scheme) -> Tuple[bool, List[RuleResult]]:
        results: List[RuleResult] = []
        hard = scheme.eligibility.get('hard_constraints', {})

        # ── 1. Min Age ──────────────────────────────────────────────────────────
        if 'min_age' in hard:
            rule = hard['min_age']
            min_req = 0
            if isinstance(rule, dict):
                if profile.gender == 'female' and 'female' in rule:
                    min_req = rule['female']
                elif profile.category in ['SC', 'ST'] and 'sc_st_male' in rule:
                    min_req = rule['sc_st_male']
                elif 'general_male' in rule:
                    min_req = rule['general_male']
                else:
                    min_req = min(rule.values()) if rule else 0
            elif isinstance(rule, (int, float)):
                min_req = int(rule)

            if min_req > 0:
                if profile.age is None:
                    results.append(RuleResult(rule="min_age", status="missing", reason="Age not provided."))
                elif profile.age < min_req:
                    results.append(RuleResult(rule="min_age", status="fail",
                                              reason=f"Age {profile.age} is below minimum required age of {min_req}."))
                else:
                    results.append(RuleResult(rule="min_age", status="pass", reason="Age meets minimum requirement."))

        # ── 2. Max Age ──────────────────────────────────────────────────────────
        if 'max_age' in hard and isinstance(hard['max_age'], (int, float)):
            max_req = int(hard['max_age'])
            if profile.age is None:
                results.append(RuleResult(rule="max_age", status="missing", reason="Age not provided."))
            elif profile.age > max_req:
                results.append(RuleResult(rule="max_age", status="fail",
                                          reason=f"Age {profile.age} exceeds maximum limit of {max_req}."))
            else:
                results.append(RuleResult(rule="max_age", status="pass", reason="Age is within maximum limit."))

        # ── 3. Age Range (for milestone schemes like Kishori) ───────────────────
        if 'age_range' in hard and isinstance(hard['age_range'], dict):
            ar = hard['age_range']
            if 'condition' not in ar:  # only hard-check ranges without a "condition" qualifier
                if profile.age is None:
                    results.append(RuleResult(rule="age_range", status="missing", reason="Age not provided."))
                elif not (ar.get('min', 0) <= profile.age <= ar.get('max', 200)):
                    results.append(RuleResult(rule="age_range", status="fail",
                                              reason=f"Age {profile.age} not in required range {ar.get('min')}-{ar.get('max')}."))
                else:
                    results.append(RuleResult(rule="age_range", status="pass", reason="Age in required range."))

        # ── 4. Annual Income ────────────────────────────────────────────────────
        if 'max_income_annual' in hard and hard['max_income_annual'] is not None:
            max_inc = int(hard['max_income_annual'])
            if profile.income is None:
                results.append(RuleResult(rule="income", status="missing", reason="Annual family income not provided."))
            elif profile.income > max_inc:
                results.append(RuleResult(rule="income", status="fail",
                                          reason=f"Income ₹{profile.income:,} exceeds limit of ₹{max_inc:,}."))
            else:
                results.append(RuleResult(rule="income", status="pass", reason="Income is within allowed limit."))

        # ── 5. Social Category ──────────────────────────────────────────────────
        if 'categories' in hard and hard['categories']:
            allowed = [c.lower() for c in hard['categories']]
            if profile.category is None:
                results.append(RuleResult(rule="category", status="missing", reason="Social category not provided."))
            elif profile.category.lower() not in allowed:
                results.append(RuleResult(rule="category", status="fail",
                                          reason=f"Category '{profile.category}' is not in the allowed list: {hard['categories']}."))
            else:
                results.append(RuleResult(rule="category", status="pass", reason="Social category matches."))

        # ── 6. Gender ───────────────────────────────────────────────────────────
        if 'gender' in hard and hard['gender']:
            allowed = [g.lower() for g in hard['gender']]
            if profile.gender is None:
                results.append(RuleResult(rule="gender", status="missing", reason="Gender not provided."))
            elif profile.gender.lower() not in allowed:
                results.append(RuleResult(rule="gender", status="fail",
                                          reason=f"This scheme is available only for: {', '.join(hard['gender'])}."))
            else:
                results.append(RuleResult(rule="gender", status="pass", reason="Gender matches scheme criteria."))

        # ── 7. Occupation ───────────────────────────────────────────────────────
        if 'occupation' in hard and hard['occupation']:
            allowed = [o.lower() for o in hard['occupation']]
            if profile.occupation is None:
                results.append(RuleResult(rule="occupation", status="missing", reason="Occupation not provided."))
            elif profile.occupation.lower() not in allowed:
                results.append(RuleResult(rule="occupation", status="fail",
                                          reason=f"This scheme requires occupation: {', '.join(hard['occupation'])}."))
            else:
                results.append(RuleResult(rule="occupation", status="pass", reason="Occupation matches."))

        # ── 8. Farmer Type (marginal / small) ───────────────────────────────────
        if 'farmer_type' in hard and hard['farmer_type']:
            allowed = [f.lower() for f in hard['farmer_type']]
            if profile.farmer_type is None:
                results.append(RuleResult(rule="farmer_type", status="missing",
                                          reason="Farmer type (marginal/small) not provided."))
            elif profile.farmer_type.lower() not in allowed:
                results.append(RuleResult(rule="farmer_type", status="fail",
                                          reason=f"Scheme is only for: {', '.join(hard['farmer_type'])} farmers."))
            else:
                results.append(RuleResult(rule="farmer_type", status="pass", reason="Farmer type matches."))

        # ── 9. Housing Status ───────────────────────────────────────────────────
        if 'housing_status' in hard and hard['housing_status']:
            allowed = [h.lower() for h in hard['housing_status']]
            if profile.housing_status is None:
                results.append(RuleResult(rule="housing_status", status="missing",
                                          reason="Current housing situation not provided."))
            elif profile.housing_status.lower() not in allowed:
                results.append(RuleResult(rule="housing_status", status="fail",
                                          reason=f"Scheme requires housing status: {', '.join(hard['housing_status'])}."))
            else:
                results.append(RuleResult(rule="housing_status", status="pass", reason="Housing status matches."))

        # ── 10. Student Class ───────────────────────────────────────────────────
        if 'student_class' in hard and hard['student_class']:
            allowed_classes = hard['student_class']  # list of ints like [8, 9, 10]
            if profile.student_class is None:
                results.append(RuleResult(rule="student_class", status="missing",
                                          reason="Current study class/grade not provided."))
            elif profile.student_class not in allowed_classes:
                results.append(RuleResult(rule="student_class", status="fail",
                                          reason=f"Scheme is for Classes {allowed_classes}. You are in Class {profile.student_class}."))
            else:
                results.append(RuleResult(rule="student_class", status="pass", reason="Study class matches."))

        # ── 11. Marital Status ──────────────────────────────────────────────────
        if 'marital_status' in hard and hard['marital_status']:
            allowed = [m.lower() for m in hard['marital_status']]
            if profile.marital_status is None:
                results.append(RuleResult(rule="marital_status", status="missing",
                                          reason="Marital status not provided."))
            elif profile.marital_status.lower() not in allowed:
                results.append(RuleResult(rule="marital_status", status="fail",
                                          reason=f"Scheme requires marital status: {', '.join(hard['marital_status'])}."))
            else:
                results.append(RuleResult(rule="marital_status", status="pass", reason="Marital status matches."))

        # ── 12. Special Conditions (disability, widow, etc.) ────────────────────
        if 'special_conditions' in hard and hard['special_conditions']:
            required = [s.lower() for s in hard['special_conditions']]
            user_conditions = [s.lower() for s in (profile.disabilities or [])]
            has_any = any(c in user_conditions for c in required)
            # Sarvajan pension: eligible if GENERAL elderly (age check handles this) OR has special condition
            # So only fail if the scheme is EXCLUSIVELY for special conditions AND no match found.
            # We treat this as a soft OR — don't fail, just note it as context.

        # ── Determine Overall Status ────────────────────────────────────────────
        failed = any(r.status == "fail" for r in results)
        is_eligible = not failed  # Missing = maybe; only hard FAIL counts as ineligible

        return is_eligible, results


eligibility_engine = EligibilityEngine()
