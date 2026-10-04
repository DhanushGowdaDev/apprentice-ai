from app.models.expertise import Expertise, Step


def test_expertise_model():
    expertise = Expertise(
        title="Motorcycle Battery Check",
        purpose="Check whether a motorcycle battery is functioning correctly.",
        when_to_use="When the motorcycle does not start.",
        tools=["multimeter"],
        preconditions=["Turn off the ignition"],
        steps=[
            Step(
                number=1,
                instruction="Set the multimeter to DC voltage.",
                rationale="The battery provides DC voltage.",
                confidence=0.95,
            )
        ],
        warnings=[
            "Do not short the battery terminals."
        ],
        common_mistakes=[
            "Using the wrong multimeter setting"
        ],
        failure_conditions=[
            "Battery voltage remains critically low"
        ],
    )

    assert expertise.title == "Motorcycle Battery Check"
    assert len(expertise.steps) == 1
    assert expertise.steps[0].confidence == 0.95