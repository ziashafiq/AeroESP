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
        )
    )


    return list(results)