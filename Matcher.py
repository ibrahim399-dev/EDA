"""
Simple, dependency-light matching engine.
Uses keyword overlap + fuzzy string similarity (difflib) so it works
without needing embeddings, API keys, or heavy ML libraries.
"""

import re
from difflib import SequenceMatcher
from knowledge_base import KNOWLEDGE_BASE

STOPWORDS = {
    "a", "an", "the", "is", "are", "do", "does", "did", "what", "how",
    "when", "where", "who", "can", "i", "you", "your", "my", "to", "for",
    "of", "in", "on", "with", "about", "me", "it", "this", "that", "will",
    "be", "and", "or", "please", "tell", "know", "get"
}


def normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> set:
    words = normalize(text).split()
    return {w for w in words if w not in STOPWORDS}


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def score_entry(user_query: str, entry: dict) -> float:
    """Score a knowledge base entry against the user's query."""
    user_tokens = tokenize(user_query)
    user_norm = normalize(user_query)

    best_score = 0.0

    # Compare against canonical question + all keyword phrasings
    candidates = [entry["question"]] + entry.get("keywords", [])

    for phrase in candidates:
        phrase_tokens = tokenize(phrase)
        phrase_norm = normalize(phrase)

        # Token overlap score (Jaccard-ish, weighted toward recall of user's words)
        if user_tokens and phrase_tokens:
            overlap = len(user_tokens & phrase_tokens)
            token_score = overlap / max(len(user_tokens), 1)
        else:
            token_score = 0.0

        # Fuzzy string similarity as a secondary signal
        fuzzy_score = similarity(user_norm, phrase_norm)

        combined = (token_score * 0.7) + (fuzzy_score * 0.3)
        best_score = max(best_score, combined)

    return best_score


def find_best_match(user_query: str, threshold: float = 0.35):
    """
    Returns (entry, score) for the best matching KB entry,
    or (None, 0) if nothing clears the threshold.
    """
    if not user_query or not user_query.strip():
        return None, 0.0

    scored = [(entry, score_entry(user_query, entry)) for entry in KNOWLEDGE_BASE]
    scored.sort(key=lambda x: x[1], reverse=True)

    best_entry, best_score = scored[0]

    if best_score >= threshold:
        return best_entry, best_score
    return None, best_score


def find_top_matches(user_query: str, n: int = 3, threshold: float = 0.2):
    """Return top-n candidate matches above a low threshold (for 'did you mean' suggestions)."""
    scored = [(entry, score_entry(user_query, entry)) for entry in KNOWLEDGE_BASE]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [(e, s) for e, s in scored[:n] if s >= threshold]
  
