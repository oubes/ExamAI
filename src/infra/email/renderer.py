# ---- Imports ---- #
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape


# ---- Paths ---- #
TEMPLATES_DIR = Path(__file__).resolve().parents[2] / "templates" / "email"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html"]),
)


# ---- YAML Loader ---- #
def load_template(template_name: str) -> dict:
    path = TEMPLATES_DIR / template_name
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---- Renderer ---- #
def render_template(template_name: str, context: dict) -> dict:

    data = load_template(template_name)

    subject = env.from_string(data["subject"]).render(**context)
    body = env.from_string(data["body"]).render(**context)
    html = env.from_string(data["html"]).render(**context)

    return {
        "subject": subject,
        "body": body,
        "html": html,
    }