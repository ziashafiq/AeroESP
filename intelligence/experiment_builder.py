from .models import (
    AIExperiment,
    AIExperimentResult,
)

from .model_comparison import (
    build_model_comparison,
)


def create_model_comparison_experiment():

    experiment = AIExperiment.objects.create(
        name="AI Provider Comparison Experiment",
        description=(
            "Automatic comparison of AI providers"
        ),
        metadata={
            "type": "model_comparison",
        },
    )


    comparison = build_model_comparison()


    for item in comparison:

        AIExperimentResult.objects.create(
            experiment=experiment,

            provider=item["provider"],

            generations=item["generations"],

            quality_score=(
                item["average_quality"]
            ),

            acceptance_rate=(
                item["acceptance_rate"]
            ),

            total_tokens=(
                item["total_tokens"]
            ),

            estimated_cost=(
                item["estimated_cost"]
            ),
        )


    return experiment