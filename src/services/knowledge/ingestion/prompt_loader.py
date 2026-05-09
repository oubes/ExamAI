"""Prompt template loading utilities."""

# ---- Imports ---- #
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Environment


# ---- Paths ---- #
PROMPTS_DIR = Path(__file__).resolve().parents[3] / "templates" / "prompts"


# ---- Jinja Environment ---- #
env = Environment(autoescape=False)


# ---- Internal Helpers ---- #
def _render_value(value: Any, context: dict[str, Any]) -> Any:
    if isinstance(value, str):
        return env.from_string(value).render(**context)

    if isinstance(value, dict):
        return {key: _render_value(item, context) for key, item in value.items()}

    if isinstance(value, list):
        return [_render_value(item, context) for item in value]

    return value


# ---- Load Template ---- #
def load_prompt_template(template_name: str) -> dict[str, Any]:
    template_path = PROMPTS_DIR / template_name

    if not template_path.exists():
        raise FileNotFoundError(f"Prompt template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle) or {}

    if not isinstance(loaded, dict):
        raise ValueError(f"Prompt template must be a mapping: {template_path}")

    return loaded


# ---- Render Template ---- #
def render_prompt_template(template_name: str, context: dict[str, Any]) -> dict[str, Any]:
    template = load_prompt_template(template_name)
    return _render_value(template, context)
