from .models import (
    AIExperiment,
)


def build_experiment_report(
    experiment_id,
):

    experiment = (
        AIExperiment.objects
        .prefetch_related(
            "results"
        )
        .get(
            id=experiment_id
        )
    )


    results = []

    for item in experiment.results.all():

        results.append(
            {
                "provider":
                    item.provider,

                "quality":
                    item.quality_score,

                "acceptance":
                    item.acceptance_rate,

                "recommendation":
                    item.recommendation,
            }
        )


    winner = None

    if results:

        winner = max(
            results,
            key=lambda x: x["quality"],
        )["provider"]


    return {
        "experiment":
            experiment.name,

        "created_at":
            experiment.created_at,

        "results":
            results,

        "winner":
            winner,
    }