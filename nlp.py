import difflib
import re


# Small synonym dictionary to improve symptom matching.
# Keys are normalized terms (stemmed), values are alternate terms we want to treat as equivalent.
_SYNONYMS = {
    "itch": ["itchy", "itchiness", "itching"],
    "rash": ["rashes", "skin rash", "skin rashes"],
    "fever": ["temperature", "high fever", "hot"],
    "cough": ["coughing", "khansi"],
    "pain": ["ache", "aching"],
    "headache": ["head pain", "sir dard"],
    "vomit": ["vomiting", "throw up"],
    "nausea": ["nauseous"],
}


def preprocess(text):
    """Lowercase, remove unwanted characters, normalize spaces."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)  # keep basic ascii alphanum
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text):
    """Split into tokens (simple whitespace)."""
    return text.split()


def _normalize_word(w: str) -> str:
    w = w.lower().strip()
    if w.endswith("ing"):
        w = w[:-3]
    if w.endswith("ed"):
        w = w[:-2]
    if w.endswith("y"):
        w = w[:-1]
    return w


def contains_keyword(text, keyword):
    """Check if keyword appears in the text.

    This matches whole words/phrases, supports fuzzy matching, and also uses
    a small synonym dictionary for common symptom variants.
    """
    text = preprocess(text)
    keyword = keyword.lower().strip()

    def phrase_in_text(txt: str, phrase: str) -> bool:
        # Exact phrase match using word boundaries
        if re.search(r"\b" + re.escape(phrase) + r"\b", txt):
            return True

        # Relaxed match: ensure each word in the phrase exists as a token.
        phrase_words = [w for w in phrase.split() if w]
        tokens = tokenize(txt)
        return all(any(normalize_token(t) == normalize_token(w) for t in tokens) for w in phrase_words)

    def normalize_token(tok: str) -> str:
        return _normalize_word(tok)

    # Multi-word phrases (e.g., "skin rash")
    if " " in keyword:
        return phrase_in_text(text, keyword)

    tokens = tokenize(text)

    # Exact token match
    if keyword in tokens:
        return True

    keyword_norm = _normalize_word(keyword)

    # Synonym match via small dictionary
    for base, variants in _SYNONYMS.items():
        if keyword_norm == base or keyword_norm in variants:
            # If the keyword matches a known synonym group, check if any variant appears.
            for v in [base] + variants:
                if phrase_in_text(text, v):
                    return True

    # Stem-normalized match (e.g., "itchy" <-> "itching")
    if any(normalize_token(tok) == keyword_norm for tok in tokens):
        return True

    # Fuzzy match for single-word keywords. Avoid matching very short tokens like
    # "and" or "hi".
    for tok in tokens:
        if len(tok) < 4 or len(keyword) < 4:
            continue

        ratio = difflib.SequenceMatcher(None, keyword, tok).ratio()
        if ratio >= 0.75:
            return True

        # Also match by stem/prefix for longer tokens (e.g., "itch" ~ "itching").
        if tok.startswith(keyword) or keyword.startswith(tok):
            return True

    return False