from fastapi import APIRouter
from pydantic import BaseModel

from app.services.compiler import compile_skill, slugify
from app.services.extractor import extract_expertise


router = APIRouter(prefix="/api/skills", tags=["skills"])


class GenerateRequest(BaseModel):
    demonstration: str


@router.post("/generate")
def generate_skill(request: GenerateRequest):
    expertise = extract_expertise(request.demonstration)

    skill_markdown = compile_skill(expertise)

    confidences = [
        step.confidence
        for step in expertise.steps
    ]

    if confidences:
        overall_confidence = sum(confidences) / len(confidences)
    else:
        overall_confidence = 0.0

    needs_review = overall_confidence < 0.8

    return {
        "status": "generated",
        "skill_id": slugify(expertise.title),
        "expertise": expertise.model_dump(),
        "skill_markdown": skill_markdown,
        "confidence": round(overall_confidence, 2),
        "needs_review": needs_review,
    }