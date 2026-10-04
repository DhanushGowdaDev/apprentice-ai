from typing import List

from pydantic import BaseModel, Field


class Step(BaseModel):
    number: int
    instruction: str
    rationale: str = ""
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class Expertise(BaseModel):
    title: str
    purpose: str
    when_to_use: str

    tools: List[str] = Field(default_factory=list)
    preconditions: List[str] = Field(default_factory=list)

    steps: List[Step] = Field(default_factory=list)

    decision_rules: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    common_mistakes: List[str] = Field(default_factory=list)
    failure_conditions: List[str] = Field(default_factory=list)

    source_language: str = "unknown"