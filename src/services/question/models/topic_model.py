# ----- IMPORTS ----- #
from src.services.question.prompts.topic_prompt import TOPIC_SYSTEM_PROMPT
from src.services.question.utils.utils import extract_json
from src.services.question.core.settings import settings


# ----- TOPIC ANALYSIS ----- #
async def analyze_topic(llm, chunk: str, state: dict):

    messages = [
        {"role": "system", "content": TOPIC_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
CURRENT TOPIC:
{state["topic"]}

TOPIC SUMMARY:
{state["topic_summary"]}

DRIFT:
{state["topic_drift_score"]}

RECENT:
{state["recent_chunks"][-3:]}

NEW CHUNK:
{chunk}
"""
        }
    ]

    result = await llm.generate(
        messages,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS
    )

    return extract_json(result)