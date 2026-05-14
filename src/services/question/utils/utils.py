# ----- IMPORTS ----- #
import re
import json
from typing import Any


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
        
# ----- HELPERS ----- #
def normalize_mcq(q: dict[str, Any]) -> dict[str, Any]:
    choices = q.get("choices")

    if isinstance(choices, list):
        q["choices"] = {
            chr(65 + i): v for i, v in enumerate(choices)
        }

    return q

# ----- MCQ VALIDATION ----- #
def validate_mcq(data: dict) -> dict:
    print("[MCQ VALIDATION] INPUT TYPE:", type(data))

    if not isinstance(data, dict):
        print("[MCQ VALIDATION] Invalid root type")
        return {"questions": []}

    questions = data.get("questions", [])
    print("[MCQ VALIDATION] RAW QUESTIONS COUNT:", len(questions) if isinstance(questions, list) else "INVALID")

    if not isinstance(questions, list):
        return {"questions": []}

    clean = []

    for idx, q in enumerate(questions):
        print(f"\n[MCQ] Processing index {idx}:", q)

        if not isinstance(q, dict):
            print("[MCQ] SKIP: not dict")
            continue

        question = q.get("question")
        choices = q.get("choices")
        answer = q.get("answer")

        print("[MCQ] question:", question)
        print("[MCQ] choices:", choices)
        print("[MCQ] answer:", answer)

        # must exist
        if not question or not choices or not answer:
            print("[MCQ] SKIP: missing required fields")
            continue

        # normalize choices
        if isinstance(choices, list) and len(choices) == 4:
            choices = {chr(65 + i): c for i, c in enumerate(choices)}
            print("[MCQ] normalized choices:", choices)

        if isinstance(choices, dict) and len(choices) != 4:
            print("[MCQ] SKIP: invalid choices dict size")
            continue

        if answer not in ["A", "B", "C", "D"]:
            print("[MCQ] SKIP: invalid answer key")
            continue

        clean.append({
            "question": question,
            "choices": choices,
            "answer": answer,
            "explanation": q.get("explanation", "")
        })

        print("[MCQ] ADDED OK")

    print("[MCQ VALIDATION] FINAL COUNT:", len(clean))
    return {"questions": clean}


# ----- WRITTEN VALIDATION ----- #
def validate_written(data: dict) -> dict:
    print("[WRITTEN VALIDATION] INPUT TYPE:", type(data))

    if not isinstance(data, dict):
        print("[WRITTEN VALIDATION] Invalid root type")
        return {"questions": []}

    questions = data.get("questions", [])
    print("[WRITTEN] RAW QUESTIONS COUNT:", len(questions) if isinstance(questions, list) else "INVALID")

    if not isinstance(questions, list):
        return {"questions": []}

    clean = []

    for idx, q in enumerate(questions):
        print(f"\n[WRITTEN] Processing index {idx}:", q)

        if not isinstance(q, dict):
            print("[WRITTEN] SKIP: not dict")
            continue

        question = q.get("question")
        answer = q.get("answer")

        print("[WRITTEN] question:", question)
        print("[WRITTEN] answer:", answer)

        if not question or not answer:
            print("[WRITTEN] SKIP: missing required fields")
            continue

        clean.append({
            "question": question,
            "answer": answer,
            "key_points": q.get("key_points", []),
            "rubric": q.get("rubric", {})
        })

        print("[WRITTEN] ADDED OK")

    print("[WRITTEN VALIDATION] FINAL COUNT:", len(clean))
    return {"questions": clean}