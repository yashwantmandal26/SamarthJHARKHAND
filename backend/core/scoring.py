from typing import List, Dict, Tuple
from backend.db.models import Scheme, UserProfile, EligibilityResult
from backend.core.eligibility_engine import eligibility_engine

class ScoringEngine:
    
    def score_and_rank(self, profile: UserProfile, schemes: List[Scheme]) -> List[EligibilityResult]:
        """
        Runs eligibility engine on all retrieved schemes and scores them.
        Sorts the result: Fully Eligible > Missing Data > Ineligible.
        Within tiers, sorts by soft score.
        """
        ranked_results = []
        
        for scheme in schemes:
            is_eligible, rule_results = eligibility_engine.check_eligibility(profile, scheme)
            
            passed = [r.rule for r in rule_results if r.status == "pass"]
            failed = [r.rule for r in rule_results if r.status == "fail"]
            missing = [r.rule for r in rule_results if r.status == "missing"]
            
            # Simple Soft Scoring
            soft_score = 0.0
            soft_rules = scheme.eligibility.get('soft_constraints', {})
            if "bpl_card" in soft_rules and profile.has_bpl_card:
                soft_score += soft_rules["bpl_card"].get("weight", 0.0)
            
            # Penalize missing data slightly in scoring to rank lower than fully exact matches
            if len(missing) > 0:
                score = 0.5 + (soft_score * 0.1) # Partial
            elif len(failed) > 0:
                score = 0.0 # Fail
            else:
                score = 1.0 + soft_score # Pass
                
            ranked_results.append(EligibilityResult(
                scheme_id=scheme.scheme_id,
                scheme_name=scheme.name,
                eligible=is_eligible and len(failed) == 0,
                score=score,
                passed_rules=passed,
                failed_rules=failed,
                missing_data=missing
            ))
            
        # Sort by score descending
        ranked_results.sort(key=lambda x: x.score, reverse=True)
        return ranked_results

scoring_engine = ScoringEngine()
