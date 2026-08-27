from .models import (
    AIExperiment,
    AIExperimentResult,
)
from .dataset_builder import (
    create_foundation_dataset,
)
from .protocol_builder import (
    create_default_protocol,
)


def create_generation_experiment(
    provider="",
):

    dataset = (
        create_foundation_dataset()
    )

    protocol = (
        create_default_protocol()
    )

    experiment = AIExperiment.objects.create(

        name=(
            "AI Question Generation Session"
        ),

        description=(
            "Tracking AI generated "
            "question drafts and teacher feedback."
        ),

        experiment_type="GENERATION",

        dataset=dataset,

        protocol=protocol,

        prompt_version=(
            "QUESTION_GENERATION_V1"
        ),

        model_version=provider,

        dataset_version=(
            dataset.version
        ),

        evaluation_method=(
            "AI quality score + teacher feedback"
        ),

    )

    AIExperimentResult.objects.create(
        experiment=experiment,

        provider=provider,

        model_name=provider,

        prompt_version=(
            "QUESTION_GENERATION_V1"
        ),

        dataset_version=(
            dataset.version
        ),

        human_score=0,

        ai_score=0,

        generations=0,

        quality_score=0,

        acceptance_rate=0,

        total_tokens=0,

        estimated_cost=0,

        recommendation=(
            "PENDING"
        ),
    )

    return experiment