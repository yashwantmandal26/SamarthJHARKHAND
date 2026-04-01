import json
from typing import List, Dict
from backend.config import settings
from backend.db.models import Scheme

class SchemeLoader:
    def __init__(self):
        self.schemes: List[Scheme] = []
        self._load_schemes()

    def _load_schemes(self):
        """Loads schemes from the JSON file into Pydantic models."""
        try:
            if settings.SCHEMES_DATA_PATH.exists():
                with open(settings.SCHEMES_DATA_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item in data:
                        self.schemes.append(Scheme(**item))
                print(f"Loaded {len(self.schemes)} schemes successfully.")
            else:
                print(f"Warning: Schemes data file not found at {settings.SCHEMES_DATA_PATH}")
        except Exception as e:
            print(f"Error loading schemes data: {e}")

    def get_all_schemes(self) -> List[Scheme]:
        return self.schemes
        
    def get_scheme_by_id(self, scheme_id: str) -> Scheme | None:
        for s in self.schemes:
            if s.scheme_id == scheme_id:
                return s
        return None

# Global instance holding all schemes in memory (only 25 items, fast and efficient)
scheme_db = SchemeLoader()
