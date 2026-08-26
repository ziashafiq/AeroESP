from .models import (
    AIExperiment,
    AIExperimentResult,
)


def log_generation_experiment(
    provider,
    quality_score,
    acceptance_rate=0,
    recommendation="",
):

    experiment = AIExperiment.objects.create(
        name="Single Question Generation Evaluation",
    )

    AIExperimentResult.objects.create(
        experiment=experiment,
        provider=provider,
        quality_score=quality_score,
        acceptance_rate=acceptance_rate,
        recommendation=recommendation,
    )

    return experiment