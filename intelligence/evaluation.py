from django.db.models import (
    Count,
    Avg,
    Q,
)

from .models import (
    AIInteractionEvent,
    AIQualitySnapshot,
    AIPromptVersion,
)


def build_prompt_evaluation():

    results = []


    prompts = (
        AIPromptVersion.objects
        .all()
    )


    for prompt in prompts:


        generation_events = (
            AIInteractionEvent.objects
            .filter(
                prompt_version=prompt.version,
                event_type=(
                    "GENERATION_SUCCESS"
                ),
            )
        )


        snapshots = (
            AIQualitySnapshot.objects
            .filter(
                event__in=generation_events
            )
        )


        total = generation_events.count()


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


        average_quality = (
            snapshots
            .aggregate(
                avg=Avg("score")
            )
            ["avg"]
        )


        if total:

            acceptance_rate = round(
                accepted / total * 100,
                2,
            )

        else:

            acceptance_rate = 0



        if (
            average_quality
            and average_quality >= 80
        ):

            recommendation = (
                "GOOD"
            )

        elif (
            average_quality
            and average_quality >= 60
        ):

            recommendation = (
                "REVIEW"
            )

        else:

            recommendation = (
                "POOR"
            )


        results.append(
            {
                "version":
                    prompt.version,

                "provider":
                    prompt.provider,

                "generations":
                    total,

                "average_quality":
                    round(
                        average_quality,
                        2
                    )
                    if average_quality
                    else 0,

                "accepted":
                    accepted,

                "edited":
                    edited,

                "rejected":
                    rejected,

                "acceptance_rate":
                    acceptance_rate,

                "recommendation":
                    recommendation,
            }
        )


    return results