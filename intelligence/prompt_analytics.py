from django.db.models import (
    Count,
    Avg,
)

from .models import (
    AIPromptVersion,
    AIInteractionEvent,
    AIQualitySnapshot,
)


def build_prompt_performance():

    result = []

    prompts = (
        AIPromptVersion.objects
        .all()
    )


    for prompt in prompts:

        events = (
            AIInteractionEvent.objects
            .filter(
                prompt_version=prompt.version,
                event_type="GENERATION_SUCCESS",
            )
        )


        snapshots = (
            AIQualitySnapshot.objects
            .filter(
                event__in=events
            )
        )


        accepted = (
            snapshots
            .filter(
                quality_data__action=(
                    "teacher_accept"
                )
            )
            .count()
        )


        edited = (
            snapshots
            .filter(
                quality_data__action=(
                    "teacher_edit"
                )
            )
            .count()
        )


        rejected = (
            snapshots
            .filter(
                quality_data__action=(
                    "teacher_reject"
                )
            )
            .count()
        )


        avg_score = (
            snapshots
            .aggregate(
                avg=Avg("score")
            )
            ["avg"]
        )


        result.append(
            {
                "version": prompt.version,

                "provider": prompt.provider,

                "generations": events.count(),

                "average_score": (
                    round(
                        avg_score,
                        2
                    )
                    if avg_score
                    else 0
                ),

                "accepted": accepted,

                "edited": edited,

                "rejected": rejected,
            }
        )


    return result