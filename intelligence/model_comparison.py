from django.db.models import (
    Avg,
    Count,
    Sum,
)

from .models import (
    AIInteractionEvent,
    AIQualitySnapshot,
)


def build_model_comparison():

    results = []


    providers = sorted(
        set(
            AIInteractionEvent.objects
            .values_list(
                "provider",
                flat=True,
            )
        )
    )


    for provider in providers:

        if not provider:
            continue


        events = (
            AIInteractionEvent.objects
            .filter(
                provider=provider,
                event_type=(
                    "GENERATION_SUCCESS"
                ),
            )
        )


        snapshots = (
            AIQualitySnapshot.objects
            .filter(
                draft__in=(
                    events
                    .values_list(
                        "draft_id",
                        flat=True,
                    )
                )
            )
        )


        generations = (
            events.count()
        )


        average_quality = (
            snapshots
            .aggregate(
                avg=Avg("score")
            )
            ["avg"]
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


        reviewed = (
            accepted
            + edited
            + rejected
        )


        acceptance_rate = 0

        if reviewed:
            acceptance_rate = round(
                accepted / reviewed * 100,
                2,
            )


        total_tokens = (
            events
            .aggregate(
                total=Sum(
                    "total_tokens"
                )
            )
            ["total"]
            or 0
        )


        estimated_cost = 0


        results.append(
            {
                "provider":
                    provider,

                "generations":
                    generations,

                "average_quality":
                    round(
                        average_quality,
                        2,
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

                "total_tokens":
                    total_tokens,

                "estimated_cost":
                    estimated_cost,
            }
        )


    return results