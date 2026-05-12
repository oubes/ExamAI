# ----- IMPORTS ----- #
from typing import Dict, List, Any


# ----- CHUNK HEADER ----- #
def print_chunk_header(i: int, state: Dict[str, Any]):
    print("\n==============================")
    print(f"CHUNK {i}")
    print("==============================")

    print("\nCHAPTER:", state.get("chapter"))
    print("TOPIC:", state.get("topic"))
    print("SKILLS:", state.get("skills"))


# ----- MCQ REPORT ----- #
def print_mcq(mcq_list: List[dict]):
    print("\n========== MCQ ==========")

    for q in mcq_list:
        print("\nQ:", q.get("question"))
        print("Difficulty:", q.get("difficulty"))

        choices = q.get("choices", {})

        if isinstance(choices, dict):
            for k, v in choices.items():
                print(f"  {k}) {v}")
        else:
            print("  [INVALID CHOICES FORMAT]")

        print("✔ Answer:", q.get("answer"))


# ----- WRITTEN REPORT ----- #
def print_written(written_list: List[dict]):
    print("\n========== WRITTEN ==========")

    for q in written_list:
        print("\nQ:", q.get("question"))
        print("Difficulty:", q.get("difficulty"))

        key_points = q.get("key_points", [])

        if isinstance(key_points, list):
            for p in key_points:
                print("-", p)
        else:
            print(key_points)


# ----- CHUNK FOOTER ----- #
def print_chunk_footer(i: int, state: Dict[str, Any]):
    print(f"\n--- Chunk {i} processed ---")
    print("Topic:", state.get("topic"))