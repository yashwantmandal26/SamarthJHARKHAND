from typing import List, Dict, Any, Tuple, Optional
from backend.db.models import UserProfile, Scheme
from pydantic import BaseModel


class RuleResult(BaseModel):
    rule: str
    status: str  # "pass", "fail", "missing"
    reason: str


class EligibilityEngine:
    """Deterministic rule engine for scheme eligibility. Checks all hard constraints."""

    def check_eligibility(self, profile: UserProfile, scheme: Scheme) -> Tuple[bool, List[RuleResult]]:
        """Fail-fast evaluation for hard constraints.

        Rules behavior:
        - If a hard rule FAILS -> return immediately as ineligible.
        - If required data is missing/invalid -> mark rule as "missing" and continue.
        - If no fails happen -> return eligible=True (even if some data is missing).
        """
        results: List[RuleResult] = []
        hard = scheme.eligibility.get('hard_constraints', {})

        # ── 1. Min Age ──────────────────────────────────────────────────────────
        if 'min_age' in hard:
            min_req = self._resolve_min_age(hard.get('min_age'), profile)
            if min_req is None:
                results.append(RuleResult(rule="min_age", status="missing", reason="Minimum age rule is not parseable."))
            elif min_req > 0:
                age = self._to_int(profile.age)
                if age is None:
                    results.append(RuleResult(rule="min_age", status="missing", reason="Age not provided."))
                elif age < min_req:
                    results.append(RuleResult(rule="min_age", status="fail", reason=f"Age {age} is below minimum required age of {min_req}."))
                    return False, results
                else:
                    results.append(RuleResult(rule="min_age", status="pass", reason="Age meets minimum requirement."))

        # ── 2. Max Age ──────────────────────────────────────────────────────────
        if 'max_age' in hard:
            max_req = self._to_int(hard.get('max_age'))
            if max_req is None:
                results.append(RuleResult(rule="max_age", status="missing", reason="Maximum age rule is not parseable."))
            else:
                age = self._to_int(profile.age)
                if age is None:
                    results.append(RuleResult(rule="max_age", status="missing", reason="Age not provided."))
                elif age > max_req:
                    results.append(RuleResult(rule="max_age", status="fail", reason=f"Age {age} exceeds maximum limit of {max_req}."))
                    return False, results
                else:
                    results.append(RuleResult(rule="max_age", status="pass", reason="Age is within maximum limit."))

        # ── 3. Age Range ────────────────────────────────────────────────────────
        if 'age_range' in hard and isinstance(hard.get('age_range'), dict):
            ar = hard['age_range']
            if 'condition' not in ar:
                min_age = self._to_int(ar.get('min'))
                max_age = self._to_int(ar.get('max'))
                age = self._to_int(profile.age)

                if age is None:
                    results.append(RuleResult(rule="age_range", status="missing", reason="Age not provided."))
                elif min_age is None or max_age is None:
                    results.append(RuleResult(rule="age_range", status="missing", reason="Age range rule is not parseable."))
                elif not (min_age <= age <= max_age):
                    results.append(RuleResult(rule="age_range", status="fail", reason=f"Age {age} not in required range {min_age}-{max_age}."))
                    return False, results
                else:
                    results.append(RuleResult(rule="age_range", status="pass", reason="Age in required range."))

        # ── 4. Annual Income ────────────────────────────────────────────────────
        if 'max_income_annual' in hard and hard.get('max_income_annual') is not None:
            max_inc = self._to_int(hard.get('max_income_annual'))
            if max_inc is None:
                results.append(RuleResult(rule="income", status="missing", reason="Income limit rule is not parseable."))
            else:
                income = self._to_int(profile.income)
                if income is None:
                    results.append(RuleResult(rule="income", status="missing", reason="Annual family income not provided."))
                elif income > max_inc:
                    results.append(RuleResult(rule="income", status="fail", reason=f"Income ₹{income:,} exceeds limit of ₹{max_inc:,}."))
                    return False, results
                else:
                    results.append(RuleResult(rule="income", status="pass", reason="Income is within allowed limit."))

        # ── 5. Social Category ──────────────────────────────────────────────────
        if 'categories' in hard and hard.get('categories'):
            allowed = self._normalize_allowed_values(hard.get('categories'))
            category = self._norm_str(profile.category)
            if category is None:
                results.append(RuleResult(rule="category", status="missing", reason="Social category not provided."))
            elif category not in allowed:
                results.append(RuleResult(rule="category", status="fail", reason=f"Category '{profile.category}' is not in the allowed list: {hard.get('categories')}."))
                return False, results
            else:
                results.append(RuleResult(rule="category", status="pass", reason="Social category matches."))

        # ── 6. Gender ───────────────────────────────────────────────────────────
        if 'gender' in hard and hard.get('gender'):
            allowed = self._normalize_allowed_values(hard.get('gender'))
            gender = self._norm_str(profile.gender)
            if gender is None:
                results.append(RuleResult(rule="gender", status="missing", reason="Gender not provided."))
            elif gender not in allowed:
                results.append(RuleResult(rule="gender", status="fail", reason=f"This scheme is available only for: {', '.join(map(str, hard.get('gender', [])))}."))
                return False, results
            else:
                results.append(RuleResult(rule="gender", status="pass", reason="Gender matches scheme criteria."))

        # ── 7. Occupation ───────────────────────────────────────────────────────
        if 'occupation' in hard and hard.get('occupation'):
            allowed = self._normalize_allowed_values(hard.get('occupation'))
            occupation = self._norm_str(profile.occupation)
            if occupation is None:
                results.append(RuleResult(rule="occupation", status="missing", reason="Occupation not provided."))
            elif occupation not in allowed:
                results.append(RuleResult(rule="occupation", status="fail", reason=f"This scheme requires occupation: {', '.join(map(str, hard.get('occupation', [])))}."))
                return False, results
            else:
                results.append(RuleResult(rule="occupation", status="pass", reason="Occupation matches."))

        # ── 8. Farmer Type ──────────────────────────────────────────────────────
        if 'farmer_type' in hard and hard.get('farmer_type'):
            allowed = self._normalize_allowed_values(hard.get('farmer_type'))
            farmer_type = self._norm_str(profile.farmer_type)
            if farmer_type is None:
                results.append(RuleResult(rule="farmer_type", status="missing", reason="Farmer type (marginal/small) not provided."))
            elif farmer_type not in allowed:
                results.append(RuleResult(rule="farmer_type", status="fail", reason=f"Scheme is only for: {', '.join(map(str, hard.get('farmer_type', [])))} farmers."))
                return False, results
            else:
                results.append(RuleResult(rule="farmer_type", status="pass", reason="Farmer type matches."))

        # ── 9. Housing Status ───────────────────────────────────────────────────
        if 'housing_status' in hard and hard.get('housing_status'):
            allowed = self._normalize_allowed_values(hard.get('housing_status'))
            housing = self._norm_str(profile.housing_status)
            if housing is None:
                results.append(RuleResult(rule="housing_status", status="missing", reason="Current housing situation not provided."))
            elif housing not in allowed:
                results.append(RuleResult(rule="housing_status", status="fail", reason=f"Scheme requires housing status: {', '.join(map(str, hard.get('housing_status', [])))}."))
                return False, results
            else:
                results.append(RuleResult(rule="housing_status", status="pass", reason="Housing status matches."))

        # ── 10. Student Class ───────────────────────────────────────────────────
        if 'student_class' in hard and hard.get('student_class'):
            allowed_classes = self._normalize_int_list(hard.get('student_class'))
            student_class = self._to_int(profile.student_class)
            if student_class is None:
                results.append(RuleResult(rule="student_class", status="missing", reason="Current study class/grade not provided."))
            elif not allowed_classes:
                results.append(RuleResult(rule="student_class", status="missing", reason="Student class rule is not parseable."))
            elif student_class not in allowed_classes:
                results.append(RuleResult(rule="student_class", status="fail", reason=f"Scheme is for Classes {allowed_classes}. You are in Class {student_class}."))
                return False, results
            else:
                results.append(RuleResult(rule="student_class", status="pass", reason="Study class matches."))

        # ── 11. Marital Status ──────────────────────────────────────────────────
        if 'marital_status' in hard and hard.get('marital_status'):
            allowed = self._normalize_allowed_values(hard.get('marital_status'))
            marital_status = self._norm_str(profile.marital_status)
            if marital_status is None:
                results.append(RuleResult(rule="marital_status", status="missing", reason="Marital status not provided."))
            elif marital_status not in allowed:
                results.append(RuleResult(rule="marital_status", status="fail", reason=f"Scheme requires marital status: {', '.join(map(str, hard.get('marital_status', [])))}."))
                return False, results
            else:
                results.append(RuleResult(rule="marital_status", status="pass", reason="Marital status matches."))

        # ── 12. Special Conditions ──────────────────────────────────────────────
        if 'special_conditions' in hard and hard.get('special_conditions'):
            required = self._normalize_allowed_values(hard.get('special_conditions'))
            user_conditions = self._normalize_allowed_values(profile.disabilities or [])
            if not user_conditions:
                results.append(RuleResult(rule="special_conditions", status="missing", reason="Special condition details not provided."))
            elif any(c in user_conditions for c in required):
                results.append(RuleResult(rule="special_conditions", status="pass", reason="Special condition requirement satisfied."))
            else:
                # Keep backward-compatible behavior: do not force fail for all schemes using special_conditions.
                results.append(RuleResult(rule="special_conditions", status="missing", reason="No matching special condition provided."))

        # No hard failure encountered.
        return True, results

    def _to_int(self, value: Any) -> Optional[int]:
        """Safely coerce scalar value to int without raising."""
        if value is None:
            return None
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            cleaned = value.strip().replace(",", "")
            if not cleaned:
                return None
            try:
                return int(float(cleaned))
            except ValueError:
                return None
        return None

    def _norm_str(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            value = str(value)
        normalized = value.strip().lower()
        return normalized if normalized else None

    def _normalize_allowed_values(self, values: Any) -> List[str]:
        if not isinstance(values, list):
            return []
        normalized: List[str] = []
        for item in values:
            v = self._norm_str(item)
            if v is not None:
                normalized.append(v)
        return normalized

    def _normalize_int_list(self, values: Any) -> List[int]:
        if not isinstance(values, list):
            return []
        normalized: List[int] = []
        for item in values:
            v = self._to_int(item)
            if v is not None:
                normalized.append(v)
        return normalized

    def _resolve_min_age(self, rule: Any, profile: UserProfile) -> Optional[int]:
        """Resolve min_age rule from scalar/dict definitions safely."""
        if isinstance(rule, dict):
            gender = self._norm_str(profile.gender)
            category = self._norm_str(profile.category)

            if gender == 'female' and 'female' in rule:
                return self._to_int(rule.get('female'))
            if category in {'sc', 'st'} and 'sc_st_male' in rule:
                return self._to_int(rule.get('sc_st_male'))
            if 'general_male' in rule:
                return self._to_int(rule.get('general_male'))

            parsed_values = [self._to_int(v) for v in rule.values()]
            parsed_values = [v for v in parsed_values if v is not None]
            return min(parsed_values) if parsed_values else None

        return self._to_int(rule)


eligibility_engine = EligibilityEngine()
