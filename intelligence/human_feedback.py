from .models import (
    AIExperimentResult,
    AIInteractionEvent,
)


def calculate_human_score(
    accepted,
    edited,
    rejected,
):

    total = (
        accepted
        + edited
        + rejected
    )

    if total == 0:
        return 0


    score = (
        accepted * 100
        +
        edited * 70
        +
        rejected * 0
    ) / total


    return round(
        score,
        2,
    )


def update_human_score(
    result_id,
    score,
):

    result = (
        AIExperimentResult.objects
        .get(
            id=result_id
        )
    )

    result.human_score = score

    result.save(
        update_fields=[
            "human_score"
        ]
    )

    return result


def calculate_from_events(events):

    accepted = 0
    edited = 0
    rejected = 0


    for event in events:

        if event.event_type == "DRAFT_ACCEPTED":
            accepted += 1

        elif event.event_type == "DRAFT_EDITED":
            edited += 1

        elif event.event_type == "DRAFT_REJECTED":
            rejected += 1


    return calculate_human_score(
        accepted,
        edited,
        rejected,
    )


def update_result_human_score_from_events(
    result_id,
    draft_id,
):

    events = (
        AIInteractionEvent.objects
        .filter(
            draft_id=draft_id
        )
    )


    score = calculate_from_events(
        events
    )


    return update_human_score(
        result_id,
        score,
    )