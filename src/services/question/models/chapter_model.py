# ----- IMPORTS ----- #
from src.services.question.prompts.chapter_prompt import CHAPTER_SYSTEM_PROMPT
from src.services.question.core.utils import extract_json
from src.services.question.core.settings import settings


# ----- CHAPTER ANALYSIS ----- #
async def analyze_chapter(llm, chunk: str, state: dict):

    messages = [
        {"role": "system", "content": CHAPTER_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
CURRENT CHAPTER:
{state["chapter"]}

CHAPTER SUMMARY:
{state["chapter_summary"]}

RECENT:
{state["recent_chunks"][-settings.RECENT_CHUNKS_LIMIT:]}

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