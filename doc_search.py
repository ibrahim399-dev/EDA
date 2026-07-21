"""
Lightweight PDF understanding: extract text, chunk it, and reuse the same
fuzzy-matching approach from matcher.py to find the most relevant excerpt
for a user's question — no embeddings or API key required.
"""

from pypdf import PdfReader
from matcher import normalize, tokenize, similarity


def extract_text_from_pdf(file_obj) -> str:
    """Extract all text from an uploaded PDF file object."""
    reader = PdfReader(file_obj)
    text_parts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            text_parts.append(text)
    return "\n".join(text_parts)


def chunk_text(text: str, chunk_size: int = 600, overlap: int = 100) -> list:
    """Split text into overlapping chunks for more precise matching."""
    text = " ".join(text.split())  # normalize whitespace
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return [c for c in chunks if c.strip()]


def find_best_chunk(user_query: str, chunks: list, threshold: float = 0.12):
    """Find the most relevant chunk of an uploaded document for a query."""
    if not chunks:
        return None, 0.0

    user_tokens = tokenize(user_query)
    user_norm = normalize(user_query)

    best_chunk, best_score = None, 0.0
    for chunk in chunks:
        chunk_tokens = tokenize(chunk)
        if user_tokens and chunk_tokens:
            overlap_score = len(user_tokens & chunk_tokens) / max(len(user_tokens), 1)
        else:
            overlap_score = 0.0
        fuzzy_score = similarity(user_norm, normalize(chunk)[:200])
        combined = (overlap_score * 0.85) + (fuzzy_score * 0.15)
        if combined > best_score:
            best_score = combined
            best_chunk = chunk

    if best_score >= threshold:
        return best_chunk, best_score
    return None, best_score
