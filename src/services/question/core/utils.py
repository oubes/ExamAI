# ----- IMPORTS ----- #
import re
import json


# ----- JSON PARSER ----- #
def extract_json(text: str) -> dict:
    if not text:
        return {}

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}

    try:
        return json.loads(match.group(0))
    except Exception:
        return {}


# ----- CHUNKING ----- #
def chunk_text(text: str, chunk_size: int = 500):
    words = text.split()
    for i in range(0, len(words), chunk_size):
        yield " ".join(words[i:i + chunk_size])