from django.db.models import (
    Avg,
    Count,
    Max,
)

from .models import (
    AIExperimentResult,
)


def build_experiment_summary(
    experiment_id,
):

    results = (
        AIExperimentResult.objects
        .filter(
            experiment_id=experiment_id
        )
        .values(
            "provider"
        )
        .annotate(
            runs=Count("id"),

            average_quality=Avg(
                "quality_score"
            ),

            average_acceptance=Avg(
                "acceptance_rate"
            ),

            recommendation=Max(
                "recommendation"
            ),

            average_ai_score=Avg(
                "ai_score"
            ),

            average_human_score=Avg(
                "human_score"
            ),
        )
    )

    summary = []
    for item in results:
        avg_ai = item["average_ai_score"] or 0
        avg_human = item["average_human_score"] or 0

        summary.append({
            "provider": item["provider"],
            "runs": item["runs"],
            "average_quality": round(item["average_quality"], 2) if item["average_quality"] else 0,
            "average_acceptance": round(item["average_acceptance"], 2) if item["average_acceptance"] else 0,
            "recommendation": item["recommendation"] or "",
            "average_ai_score": round(avg_ai, 2),
            "average_human_score": round(avg_human, 2),
            "ai_human_gap": round(abs(avg_ai - avg_human), 2),
        })

    return summary