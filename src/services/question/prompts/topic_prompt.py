# ----- TOPIC PROMPT ----- #
TOPIC_SYSTEM_PROMPT = """
================ RULES =================

1. Always infer the most precise possible topic for the chunk.
2. Topic MUST be a narrow semantic unit, not a general category.
3. Topic should describe a concrete aspect, mechanism, event, or sub-process.
4. Avoid abstract or high-level labels.
   - BAD: "Politics", "Military", "Economy"
   - GOOD: "Military consolidation of Free Officers after 1952 coup"
5. Prefer multi-token descriptive phrases (4–12 words).
6. Topic must be grounded strictly in the chunk content.
7. Must NEVER return null topic.
8. Allow gradual drift across adjacent chunks.
9. Output valid JSON ONLY.

================ GRANULARITY RULE =================

10. Topic must represent ONE of:
   - event phase
   - policy mechanism
   - actor-specific action
   - time-bounded process

================ OUTPUT =================

{
  "decision": "same_topic | new_topic",
  "topic_name": "string (highly specific semantic phrase)",
  "confidence": float,
  "topic_drift": float,
  "reason": "short explanation"
}
"""