from typing import List, Optional
from backend.db.models import Scheme
from backend.data.loader import scheme_db

class RetrievalEngine:
    """Filters schemes based on direct keywords or categories."""

    def search_schemes(self, query: str = "", category: Optional[str] = None) -> List[Scheme]:
        """Simple retrieval combining exact category match and substring search in name/tags/description"""
        all_schemes = scheme_db.get_all_schemes()
        results = []
        
        q_lower = query.lower() if query else ""
        
        for scheme in all_schemes:
            # 1. Filter by category
            if category and scheme.category.lower() != category.lower():
                continue
                
            # 2. Keyword Filter (if query is provided)
            # Find in name, description, tags, department
            if q_lower:
                text_content = f"{scheme.name} {scheme.name_hindi} {scheme.description} {' '.join(scheme.tags)} {scheme.department}".lower()
                if q_lower not in text_content:
                    # Very basic "bag of words" fuzziness
                    query_words = set(q_lower.split())
                    content_words = set(text_content.replace(',', '').split())
                    if not query_words.intersection(content_words):
                        continue # Does not match any word

            results.append(scheme)
            
        return results

retrieval_engine = RetrievalEngine()
