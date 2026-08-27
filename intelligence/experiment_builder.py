from .models import (
    AIExperiment,
    AIExperimentResult,
)

from .model_comparison import (
    build_model_comparison,
)

from .dataset_builder import (
    create_foundation_dataset,
)

from .protocol_builder import (
    create_default_protocol,
)


def create_model_comparison_experiment():

    dataset = create_foundation_dataset()
    protocol = create_default_protocol()

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

        dataset=dataset,

        protocol=protocol,

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

            generations=item["generations"],

            quality_score=(
                item["average_quality"]
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