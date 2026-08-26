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
        summary.append({
            "provider": item["provider"],
            "runs": item["runs"],
            "average_quality": round(item["average_quality"], 2) if item["average_quality"] else 0,
            "average_acceptance": round(item["average_acceptance"], 2) if item["average_acceptance"] else 0,
            "recommendation": item["recommendation"] or "",
            "average_ai_score": round(item["average_ai_score"], 2) if item["average_ai_score"] else 0,
            "average_human_score": round(item["average_human_score"], 2) if item["average_human_score"] else 0,
        })

    return summary