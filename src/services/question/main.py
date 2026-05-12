# ----- IMPORTS ----- #
import asyncio
from langchain_community.document_loaders import PyMuPDFLoader

from src.core.di.llm import get_llm_service
from src.services.question.core.utils import chunk_text
from src.services.question.core.state import state
from src.services.question.core.settings import settings

from src.services.question.pipeline import update_state
from src.services.question.models.chapter_model import analyze_chapter
from src.services.question.models.topic_model import analyze_topic
from src.services.question.models.skills_model import extract_skills


# ----- MAIN LOOP ----- #
async def main():

    llm = await get_llm_service()

    loader = PyMuPDFLoader(settings.get_file_path())
    docs = loader.load()

    text = "\n".join(d.page_content for d in docs)
    chunks = list(chunk_text(text, settings.CHUNK_SIZE))

    print(f"Chunks: {len(chunks)}")

    for i, chunk in enumerate(chunks):

        chapter_pred = await analyze_chapter(llm, chunk, state)
        topic_pred = await analyze_topic(llm, chunk, state)

        update_state(chapter_pred, topic_pred, chunk)

        if state["topic"] and not state["skills"]:
            skills_resp = await extract_skills(
                llm,
                state["topic"], # type: ignore
                state["topic_summary"] # type: ignore
            )
            state["skills"] = skills_resp.get("skills", [])

        print(f"\n{'-'*20} Chunk {i} {'-'*20}")
        print(f"Chunk {i}")
        print("Chapter:", state["chapter"])
        print("Topic:", state["topic"])
        print("Skills:", state["skills"])
        print("Drift:", state["topic_drift_score"])


# ----- ENTRY POINT ----- #
if __name__ == "__main__":
    asyncio.run(main())