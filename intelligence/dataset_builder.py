from .models import AIEvaluationDataset


def create_foundation_dataset():

    dataset, created = (
        AIEvaluationDataset.objects.get_or_create(
            version="FOUNDATION_V1",

            defaults={
                "name": (
                    "Aerospace English "
                    "Evaluation Dataset"
                ),

                "description": (
                    "Dataset for evaluating "
                    "AI generated aerospace "
                    "English questions."
                ),

                "domain": (
                    "Aerospace English"
                ),

                "size": 100,
            },
        )
    )

    return dataset