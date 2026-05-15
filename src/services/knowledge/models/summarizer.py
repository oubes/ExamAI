# ----- IMPORTS ----- #
from src.services.knowledge.prompts.summarizer import SUMMARY_SYSTEM_PROMPT
from src.services.knowledge.utils.utils import extract_json, validate_summary


# ----- SUMMARY GENERATION ----- #
async def generate_summary(
    llm,
    chunk: str
):

    messages = [
        {
            "role": "system",
            "content": SUMMARY_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""
TEXT CHUNK:
{chunk}
"""
        }
    ]

    result = await llm.generate(
        messages,
        temperature=0.1,
        max_tokens=400
    )

    raw = extract_json(result)
    return validate_summary(raw)