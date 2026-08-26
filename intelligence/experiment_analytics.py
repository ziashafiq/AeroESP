from django.db.models import Avg, Count

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
    )


    summary = (
        results
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
        )
    )


    return list(summary)