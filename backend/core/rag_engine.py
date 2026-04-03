"""
RAG (Retrieval Augmented Generation) Engine for Pure AI Assistant.

This module implements a keyword + TF-IDF-inspired retrieval pipeline
that fetches the most relevant scheme data and builds rich context
for the LLM to answer any user question comprehensively.
"""

import json
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from backend.data.loader import scheme_db
from backend.db.models import Scheme


class RAGEngine:
    """Retrieval-Augmented Generation engine for scheme knowledge."""

    def __init__(self):
        self._build_index()

    def _build_index(self):
        """Build an inverted index from all scheme data for fast retrieval."""
        self.documents: List[Dict[str, Any]] = []
        self.inverted_index: Dict[str, List[int]] = {}
        self.doc_lengths: List[int] = []

        schemes = scheme_db.get_all_schemes()

        for idx, scheme in enumerate(schemes):
            # Build a rich text document from all scheme fields
            doc_text = self._scheme_to_text(scheme)
            tokens = self._tokenize(doc_text)

            self.documents.append({
                "idx": idx,
                "scheme": scheme,
                "text": doc_text,
                "tokens": tokens,
                "token_counts": Counter(tokens),
            })
            self.doc_lengths.append(len(tokens))

            # Inverted index
            for token in set(tokens):
                if token not in self.inverted_index:
                    self.inverted_index[token] = []
                self.inverted_index[token].append(idx)

        self.avg_doc_length = sum(self.doc_lengths) / max(len(self.doc_lengths), 1)
        print(f"[RAG] Built index over {len(self.documents)} schemes, {len(self.inverted_index)} unique tokens.")

    def _scheme_to_text(self, scheme: Scheme) -> str:
        """Convert a scheme into a searchable text document."""
        parts = [
            scheme.name,
            scheme.name_hindi,
            scheme.description,
            scheme.department,
            scheme.category,
            " ".join(scheme.tags),
        ]

        # Eligibility info
        hard = scheme.eligibility.get("hard_constraints", {})
        if hard:
            if "categories" in hard:
                parts.append(f"categories: {', '.join(hard['categories'])}")
            if "gender" in hard:
                parts.append(f"gender: {', '.join(hard['gender'])}")
            if "occupation" in hard:
                parts.append(f"occupation: {', '.join(hard['occupation'])}")
            if "max_income_annual" in hard and hard["max_income_annual"]:
                parts.append(f"max income: {hard['max_income_annual']}")
            if "min_age" in hard:
                parts.append(f"min age: {hard['min_age']}")
            if "max_age" in hard:
                parts.append(f"max age: {hard['max_age']}")
            if "housing_status" in hard:
                parts.append(f"housing: {', '.join(hard['housing_status'])}")
            if "farmer_type" in hard:
                parts.append(f"farmer type: {', '.join(hard['farmer_type'])}")
            if "student_class" in hard:
                parts.append(f"student class: {hard['student_class']}")

        # Benefits info
        benefits = scheme.benefits
        if benefits:
            parts.append(str(benefits.get("description", "")))
            if benefits.get("amount"):
                parts.append(f"amount: {benefits['amount']}")
            if benefits.get("frequency"):
                parts.append(f"frequency: {benefits['frequency']}")

        # Documents
        for doc in scheme.documents_required:
            parts.append(doc.get("name", ""))

        # Application process
        app = scheme.application_process
        if app:
            if app.get("online_url"):
                parts.append(f"online: {app['online_url']}")
            for step in app.get("offline_steps", []):
                parts.append(step)

        return " ".join(parts)

    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenizer: lowercase, split on non-alphanumeric, filter stopwords."""
        import re
        tokens = re.findall(r'[a-zA-Z0-9\u0900-\u097F]+', text.lower())
        # Basic stopwords
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "shall", "can", "and", "but", "or", "nor",
            "not", "no", "in", "on", "at", "by", "for", "to", "of", "with",
            "from", "as", "it", "its", "this", "that", "these", "those",
            "up", "out", "if", "so", "than", "too", "very",
            "ke", "ki", "ka", "se", "mein", "hai", "hain", "ko", "par",
            "aur", "ya", "jo", "ye", "wo", "yeh",
        }
        return [t for t in tokens if t not in stopwords and len(t) > 1]

    def _bm25_score(self, query_tokens: List[str], doc_idx: int, k1: float = 1.5, b: float = 0.75) -> float:
        """BM25 scoring for a document against query tokens."""
        doc = self.documents[doc_idx]
        score = 0.0
        N = len(self.documents)

        for token in query_tokens:
            if token not in self.inverted_index:
                continue

            df = len(self.inverted_index[token])  # document frequency
            idf = math.log((N - df + 0.5) / (df + 0.5) + 1)

            tf = doc["token_counts"].get(token, 0)
            dl = self.doc_lengths[doc_idx]

            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * dl / self.avg_doc_length)

            score += idf * (numerator / denominator)

        return score

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[Scheme, float]]:
        """Retrieve the most relevant schemes for a query using BM25."""
        query_tokens = self._tokenize(query)
        if not query_tokens:
            # Return a sample of schemes if no meaningful query
            return [(doc["scheme"], 0.0) for doc in self.documents[:top_k]]

        # Get candidate documents (those containing at least one query token)
        candidate_docs = set()
        for token in query_tokens:
            if token in self.inverted_index:
                candidate_docs.update(self.inverted_index[token])

        if not candidate_docs:
            # Fallback: return top schemes by category match
            return [(doc["scheme"], 0.0) for doc in self.documents[:top_k]]

        # Score all candidates
        scored = []
        for doc_idx in candidate_docs:
            score = self._bm25_score(query_tokens, doc_idx)
            scored.append((doc_idx, score))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_idx, score in scored[:top_k]:
            results.append((self.documents[doc_idx]["scheme"], score))

        return results

    # Occupation keyword mapping for detecting user's occupation from queries
    OCCUPATION_KEYWORDS = {
        "fisherman": ["fisherman", "fishermen", "fishing", "machhli", "machli", "matsya", "machuara", "machhua", "fish"],
        "farmer": ["farmer", "kisan", "kisaan", "kheti", "farming", "krishi", "fasal", "khet"],
        "student": ["student", "padhai", "school", "college", "vidyarthi", "chhatra"],
        "artisan": ["artisan", "karigar", "handicraft", "vishwakarma", "craftsman"],
        "labourer": ["labourer", "laborer", "worker", "mazdoor", "majdoor", "shramik"],
        "self_employed": ["self_employed", "business", "vyapari", "dukandaar", "shop"],
        "unemployed": ["unemployed", "berojgar", "berozgar", "jobless"],
    }

    def _detect_user_occupation(self, query: str) -> str:
        """Detect occupation keywords from the user's query."""
        query_lower = query.lower()
        for occupation, keywords in self.OCCUPATION_KEYWORDS.items():
            for kw in keywords:
                if kw in query_lower:
                    return occupation
        return ""

    def _classify_scheme_relevance(self, scheme: 'Scheme', user_occupation: str) -> str:
        """Classify how relevant a scheme is to the user's occupation."""
        hard = scheme.eligibility.get("hard_constraints", {})
        scheme_occupations = hard.get("occupation", [])

        if not user_occupation:
            return "RETRIEVED"  # No occupation detected, neutral label

        if not scheme_occupations:
            # No occupation restriction = universal scheme
            return "⚠️ GENERAL/UNIVERSAL (no occupation restriction — open to all)"

        # Check if user's occupation is in the scheme's eligible occupations
        if user_occupation in [o.lower() for o in scheme_occupations]:
            return "✅ DIRECTLY RELEVANT (occupation matches eligibility)"
        else:
            return f"❌ NOT RELEVANT (requires occupation: {', '.join(scheme_occupations)}, but user is: {user_occupation})"

    def build_context(self, query: str, chat_history: List[Dict[str, str]] = None, top_k: int = 5) -> str:
        """Build rich LLM context from retrieved schemes.
        
        This is the core RAG function — retrieves relevant schemes
        and formats them into a detailed context block for the LLM.
        Includes occupation-based relevance classification.
        """
        # For occupation detection: use all recent user messages so we don't forget their profile
        occupation_text_pool = query
        if chat_history:
            recent_user_msgs = [m["content"] for m in chat_history[-4:] if m["role"] == "user"]
            occupation_text_pool = " ".join(recent_user_msgs + [query])

        user_occupation = self._detect_user_occupation(occupation_text_pool)

        # For BM25 retrieval: prioritize current query to prevent context pollution
        bm25_query = query
        # If query is extremely short (e.g., "what about me?"), we add the immediate previous user message
        if chat_history and len(query.split()) <= 3:
            for m in reversed(chat_history):
                if m["role"] == "user":
                    bm25_query = f"{m['content']} {query}"
                    break
        
        # If an occupation is found, inject it so those schemes score higher (optional, helps recall)
        if user_occupation and user_occupation not in bm25_query.lower():
            bm25_query += f" {user_occupation}"

        retrieved = self.retrieve(bm25_query, top_k=top_k)

        if not retrieved or all(score == 0.0 for _, score in retrieved):
            return "NO RELEVANT SCHEMES FOUND IN THE DATABASE FOR THIS QUERY."



        context_parts = [
            f"=== RETRIEVED SCHEME KNOWLEDGE (Top {len(retrieved)} matches) ===\n"
        ]

        if user_occupation:
            context_parts.append(
                f"⚡ DETECTED USER OCCUPATION: {user_occupation}\n"
                f"⚡ IMPORTANT: Only recommend schemes marked as ✅ DIRECTLY RELEVANT or ⚠️ GENERAL/UNIVERSAL.\n"
                f"⚡ Do NOT recommend schemes marked as ❌ NOT RELEVANT.\n"
            )

        # Filter out extreme low-scoring noise to save LLM context window/speed
        max_score = max(score for _, score in retrieved) if retrieved else 0
        min_threshold = max(1.0, max_score * 0.3)
        filtered_retrieved = [(s, sc) for s, sc in retrieved if sc >= min_threshold]

        if not filtered_retrieved:
            return "NO DIRECTLY RELEVANT SCHEMES FOUND."

        for i, (scheme, score) in enumerate(filtered_retrieved, 1):
            hard = scheme.eligibility.get("hard_constraints", {})
            benefits = scheme.benefits

            # Classify relevance
            relevance_tag = self._classify_scheme_relevance(scheme, user_occupation)

            # Build eligibility summary
            elig_parts = []
            if hard.get("min_age"):
                elig_parts.append(f"Min Age: {hard['min_age']}")
            if hard.get("max_age"):
                elig_parts.append(f"Max Age: {hard['max_age']}")
            if hard.get("max_income_annual"):
                elig_parts.append(f"Max Income: ₹{hard['max_income_annual']:,}/year")
            if hard.get("categories"):
                elig_parts.append(f"Categories: {', '.join(hard['categories'])}")
            if hard.get("gender"):
                elig_parts.append(f"Gender: {', '.join(hard['gender'])}")
            if hard.get("occupation"):
                elig_parts.append(f"Occupation: {', '.join(hard['occupation'])}")
            if hard.get("farmer_type"):
                elig_parts.append(f"Farmer Type: {', '.join(hard['farmer_type'])}")
            if hard.get("housing_status"):
                elig_parts.append(f"Housing: {', '.join(hard['housing_status'])}")
            if hard.get("student_class"):
                elig_parts.append(f"Student Class: {hard['student_class']}")

            # Build docs summary
            docs = [d.get("name", "") for d in scheme.documents_required[:5]]

            # Application process
            app = scheme.application_process
            app_info = ""
            if app:
                if app.get("online_url"):
                    app_info += f"Online: {app['online_url']}"
                steps = app.get("offline_steps", [])
                if steps:
                    app_info += f"\nSteps: {'; '.join(steps[:3])}"

            context_parts.append(f"""--- SCHEME {i}: {scheme.name} ({scheme.name_hindi}) ---
RELEVANCE: {relevance_tag}
ID: {scheme.scheme_id}
Department: {scheme.department}
Category: {scheme.category}
Description: {scheme.description}
Relevance Score: {score:.2f}

ELIGIBILITY:
{chr(10).join('  • ' + e for e in elig_parts) if elig_parts else '  No specific hard constraints.'}

BENEFITS:
  Type: {benefits.get('type', 'N/A')}
  Amount: {'₹' + str(benefits['amount']) if benefits.get('amount') else 'Varies'}
  Frequency: {benefits.get('frequency', 'N/A')}
  Details: {benefits.get('description', 'N/A')}

DOCUMENTS NEEDED:
  {', '.join(docs) if docs else 'N/A'}

HOW TO APPLY:
  {app_info if app_info else 'Contact local government office.'}

""")

        context_parts.append("=== END OF RETRIEVED KNOWLEDGE ===")
        return "\n".join(context_parts)


# Global instance
rag_engine = RAGEngine()
