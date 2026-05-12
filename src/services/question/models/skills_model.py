# ----- IMPORTS ----- #
from src.services.question.prompts.skills_prompt import SKILLS_SYSTEM_PROMPT
from src.services.question.core.utils import extract_json
from src.services.question.core.settings import settings


# ----- SKILL EXTRACTION ----- #
async def extract_skills(llm, topic: str, topic_summary: str):

    messages = [
        {"role": "system", "content": SKILLS_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
TOPIC:
{topic}

SUMMARY:
{topic_summary}
"""
        }
    ]

    result = await llm.generate(
        messages,
        temperature=settings.TEMPERATURE,
        max_tokens=settings.MAX_TOKENS
    )

    return extract_json(result)