from pathlib import Path

from app.models.expertise import Expertise
from app.services.gemma import generate_json


PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "prompts" / "extraction.txt"
)


def extract_expertise(demonstration: str) -> Expertise:
    template = PROMPT_PATH.read_text(encoding="utf-8")

    prompt = template.replace(
        "{demonstration}",
        demonstration,
    )

    result = generate_json(prompt)

    return Expertise.model_validate(result)