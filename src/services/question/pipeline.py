# ----- IMPORTS ----- #
from src.services.question.core.state import state
from src.services.question.core.settings import settings


# ----- STATE UPDATE ----- #
def update_state(chapter_pred: dict, topic_pred: dict, chunk: str):

    drift = topic_pred.get("topic_drift", 0.0)
    state["topic_drift_score"] = state["topic_drift_score"] * 0.7 + drift * 0.3 # type: ignore

    is_new_chapter = (
        chapter_pred.get("decision") == "new_chapter"
        and chapter_pred.get("confidence", 0) >= settings.CHAPTER_THRESHOLD
    )

    is_new_topic = (
        topic_pred.get("decision") == "new_topic"
        and topic_pred.get("confidence", 0) >= settings.TOPIC_THRESHOLD
    )

    # ----- CHAPTER ----- #
    if is_new_chapter:
        state["chapter"] = chapter_pred.get("chapter_name")
        state["chapter_summary"] = chunk
        state["topic_summary"] = chunk
        state["topic_drift_score"] = 0.0

        state["topic"] = topic_pred.get("topic_name") or state["topic"]
        state["skills"] = []

    else:

        # ----- TOPIC ----- #
        if is_new_topic or state["topic_drift_score"] > settings.DRIFT_THRESHOLD:
            state["topic"] = topic_pred.get("topic_name")
            state["topic_summary"] = chunk
            state["topic_drift_score"] = 0.0
            state["skills"] = []
        else:
            state["topic_summary"] += " " + chunk # type: ignore
            state["chapter_summary"] += " " + chunk # type: ignore

    # ----- BUFFER ----- #
    state["recent_chunks"].append(chunk) # type: ignore

    if len(state["recent_chunks"]) > settings.RECENT_CHUNKS_LIMIT: # type: ignore
        state["recent_chunks"].pop(0) # type: ignore