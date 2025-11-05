# textfixer/services/ollama.py
from __future__ import annotations
import json
import httpx
from django.conf import settings

SYSTEM_PROMPT = (
    "You are a text normalizer.\n"
    "Follow these rules:\n"
    "(1) Restore punctuation and capitalization.\n"
    "(2) .\n"
    "(3) Do NOT add, paraphrase, summarize, or translate. Keep the output in the SAME language as the input text.\n"
    'Return STRICT JSON only: {"text":"..."}'
)

def fix_with_ollama(raw_text: str, book_hint: str | None = None) -> str:
    append_text("text.txt", raw_text)
    return raw_text

    user_obj = {"text": raw_text}
    if book_hint:
        user_obj["book_hint"] = book_hint
    """Call Ollama /api/chat and return the normalized text. Falls back to input on any error."""
    payload = {
        "model": getattr(settings, "OLLAMA_MODEL", "qwen3:8b-q8_0"),
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_obj, ensure_ascii=False)},
        ],
        "options": {          # minimize “thinking”
            "temperature": 0.1,
            "top_p": 0.9,
            "seed": 42,
            "num_predict": max(32, min(256, len(raw_text) + 16)),
        },
        "stream": False,
        "format": "json",  # ask for strict JSON
        "chat_template_kwargs": {"enable_thinking": True}
    }

    try:
        with httpx.Client(timeout=getattr(settings, "OLLAMA_TIMEOUT", 30.0)) as client:
            r = client.post(getattr(settings, "OLLAMA_URL", "http://127.0.0.1:11434/api/chat"), json=payload)
            r.raise_for_status()
            data = r.json()
        content = (data.get("message") or {}).get("content", "")
        print(data)
        # Prefer strict JSON; if not, accept plain text
        try:
            obj = json.loads(content)
            text = (obj.get("text") or "").strip()
            return text or raw_text
        except Exception:
            # Model returned plain text; use it
            return content.strip() or raw_text

    except Exception:
        # Network/HTTP/model errors → safe fallback
        return raw_text

def append_text(path, text):
    with open(path, "a", encoding="utf-8") as f:
        return f.write(text.rstrip("\n") + "\n")
