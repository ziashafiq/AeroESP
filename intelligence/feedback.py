from django.db.models import Count, Avg

from .models import (
    AIQualitySnapshot,
    AIInteractionEvent,
)


def build_ai_feedback_summary():

    total_snapshots = (
        AIQualitySnapshot.objects.count()
    )


    accepted = (
        AIQualitySnapshot.objects
        .filter(
            quality_data__action="teacher_accept"
        )
        .count()
    )


    rejected = (
        AIQualitySnapshot.objects
        .filter(
            quality_data__action="teacher_reject"
        )
        .count()
    )


    edited = (
        AIQualitySnapshot.objects
        .filter(
            quality_data__action="teacher_edit"
        )
        .count()
    )


    average_score = (
        AIQualitySnapshot.objects
        .aggregate(
            avg=Avg("score")
        )
        [
            "avg"
        ]
    )


    providers = (
        AIInteractionEvent.objects
        .values("provider")
        .annotate(
            total=Count("id")
        )
        .order_by(
            "-total"
        )
    )


    return {

        "total_feedback": total_snapshots,

        "accepted": accepted,

        "edited": edited,

        "rejected": rejected,

        "average_score": (
            round(
                average_score,
                2
            )
            if average_score
            else 0
        ),

        "providers": list(
            providers
        ),
    }