# backend/ingest/token_utils.py

import textwrap

def chunk_text(text, max_tokens=400):
    """
    Roughly chunks text to about max_tokens using simple heuristics.
    Gemini supports ~100K, but for semantic embeddings 400–600 is optimal.
    """
    return textwrap.wrap(text, width=max_tokens)

