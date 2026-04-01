import json
from backend.llm.client import llm_client
from backend.llm.prompts import Prompts
from pydantic import BaseModel

class ExplanationGenerator:
    """Uses LLM to turn deterministic results into human-friendly text."""

    async def generate_explanation(self, scheme_name: str, profile_dict: dict, passed: list, failed: list, missing: list) -> str:
        prompt = Prompts.EXPLANATION_PROMPT.format(
            scheme_name=scheme_name,
            age=profile_dict.get('age', 'Unknown'),
            income=profile_dict.get('income', 'Unknown'),
            category=profile_dict.get('category', 'Unknown'),
            passed=", ".join(passed) if passed else "None",
            failed=", ".join(failed) if failed else "None",
            missing=", ".join(missing) if missing else "None"
        )
        
        response = await llm_client.generate_response(prompt)
        return response

explanation_generator = ExplanationGenerator()
