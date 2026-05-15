# ----- IMPORTS ----- #
import json
import re
from typing import Any


# ----- JSON EXTRACTOR ----- #
def extract_json(text: str) -> dict[str, Any]:
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    # Try direct parse first
    try:
        return json.loads(text)
    except Exception:
        pass

    # ---- Fallback to regex extraction ---- #
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM output")

    json_str = match.group(0)

    try:
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Invalid JSON extracted: {str(e)}")
    
# ----- IMPORTS ----- #
from typing import Dict, Any


# ----- SUMMARY VALIDATOR ----- #
def validate_summary(data: dict[str, Any]) -> dict[str, str]:
    """
    Validate semantic summary output structure.
    """

    if not isinstance(data, dict):
        raise ValueError("Output must be a dictionary")

    if "summary" not in data:
        raise ValueError("Missing required field: summary")

    summary = data["summary"]

    if not isinstance(summary, str):
        raise ValueError("summary must be a string")

    summary = summary.strip()

    if len(summary) == 0:
        raise ValueError("summary cannot be empty")

    # optional: enforce max size guardrail
    if len(summary) > 5000:
        raise ValueError("summary too large")

    return {
        "summary": summary
    }