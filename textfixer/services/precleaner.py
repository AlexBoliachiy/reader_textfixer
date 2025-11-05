# textfixer/services/precleaner.py
import os
import re
from typing import Optional

SMALL = {"a","an","and","the","of","in","on","to","for","at","by"}

def _titlecase(s: str) -> str:
    parts = [p for p in re.split(r"[\s_]+", s.strip()) if p]
    out = []
    for i, w in enumerate(parts):
        w = re.sub(r"[^\w'-]+", "", w)              # strip punctuation
        if not w: 
            continue
        ww = w.lower()
        if i > 0 and ww in SMALL:
            out.append(ww)
        else:
            out.append(ww[:1].upper() + ww[1:])
    return " ".join(out)

def derive_book_hint(folder: Optional[str], filename: Optional[str]) -> Optional[str]:
    """
    Heuristics:
    - Prefer folder name; else use filename (sans extension).
    - Drop bracketed/parenthetical bits, common chapter/volume tokens and trailing numbers.
    - Titlecase nicely.
    """
    candidate = (folder or "") or (os.path.splitext(filename or "")[0])
    candidate = candidate.strip()
    if not candidate:
        return None

    # remove bracketed info and common noise
    candidate = re.sub(r"[\[\(\{].*?[\]\)\}]", " ", candidate)
    candidate = re.sub(r"(?i)\b(ch(ap(ter)?)?|vol(ume)?|part|book|episode|ep)\.?-?\s*\d+\b", " ", candidate)
    candidate = re.sub(r"[_\-\.]+", " ", candidate)
    candidate = re.sub(r"\b\d{1,4}\b", " ", candidate)   # stand-alone numbers (years/chapters)
    candidate = re.sub(r"\s{2,}", " ", candidate).strip()

    # very short or generic → ignore
    if len(candidate) < 3:
        return None

    return _titlecase(candidate)
