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
            "Comparison of AI providers "
            "for aerospace question generation."
        ),

        prompt_version=(
            "QUESTION_GENERATION_V1"
        ),

        model_version=(
            "MULTI_PROVIDER"
        ),

        dataset_version=(
            "FOUNDATION_V1"
        ),

        evaluation_method=(
            "AI quality score + teacher feedback"
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

            model_name=(
                item.get(
                    "model_name",
                    "",
                )
            ),

            prompt_version=(
                "QUESTION_GENERATION_V1"
            ),

            dataset_version=(
                "FOUNDATION_V1"
            ),

            ai_score=(
                item.get(
                    "average_quality",
                    0,
                )
            ),

            human_score=(
                item.get(
                    "human_score",
                    0,
                )
            ),

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

            recommendation=item.get(
                "recommendation",
                "",
            ),
        )


    return experiment