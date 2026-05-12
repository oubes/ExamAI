# ----- IMPORTS ----- #
from src.services.question.prompts.written_prompt import WRITTEN_SYSTEM_PROMPT
from src.services.question.utils.utils import extract_json
from src.services.question.core.difficulty import get_difficulty_config


# ----- WRITTEN GENERATION ----- #
async def generate_written(llm, topic: str, topic_summary: str, difficulty: str):

    config = get_difficulty_config(difficulty)

    messages = [
        {
            "role": "system",
            "content": WRITTEN_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"""
TOPIC:
{topic}

TOPIC SUMMARY:
{topic_summary}

DIFFICULTY:
{difficulty}
"""
        }
    ]

    result = await llm.generate(
        messages,
        temperature=config["temperature"],
        max_tokens=config["max_tokens"]
    )

    return extract_json(result)