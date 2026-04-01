from typing import Dict, Any, List
from backend.db.models import UserProfile, EligibilityResult
from backend.core.scoring import scoring_engine
from backend.data.loader import scheme_db

class WhatIfSimulator:
    """Allows users to simulate eligibility changes based on hypothetical data."""

    def run_simulation(self, current_profile: UserProfile, overrides: Dict[str, Any]) -> List[EligibilityResult]:
        """
        Creates a temporary simulated profile, applies overrides (like changing income or age),
        and returns the new eligibility map for all schemes.
        """
        sim_profile = current_profile.model_copy(update=overrides)
        all_schemes = scheme_db.get_all_schemes()
        
        simulated_results = scoring_engine.score_and_rank(sim_profile, all_schemes)
        
        return simulated_results

what_if_simulator = WhatIfSimulator()
