from app.models.expertise import Expertise, Step
from app.services.compiler import compile_skill


def test_compile_skill():
    expertise = Expertise(
        title="Motorcycle Battery Check",
        purpose="Check a motorcycle battery.",
        when_to_use="When a motorcycle does not start.",
        tools=["multimeter"],
        steps=[
            Step(
                number=1,
                instruction="Set the multimeter to DC voltage.",
                rationale="The battery provides DC voltage.",
                confidence=0.95,
            ),
            Step(
                number=2,
                instruction="Measure the battery voltage.",
                rationale="This determines the battery condition.",
                confidence=0.92,
            ),
        ],
        warnings=[
            "Do not short the battery terminals."
        ],
    )

    markdown = compile_skill(expertise)

    assert "# Motorcycle Battery Check" in markdown
    assert "## Purpose" in markdown
    assert "## Procedure" in markdown
    assert "Set the multimeter to DC voltage." in markdown
    assert "## Safety Warnings" in markdown