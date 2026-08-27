from .models import AIEvaluationProtocol


def create_default_protocol():

    protocol, created = (
        AIEvaluationProtocol.objects.get_or_create(
            version="EVAL_V1",

            defaults={
                "name": (
                    "AI Question Generation "
                    "Evaluation Protocol"
                ),

                "description": (
                    "Evaluation protocol for "
                    "AI generated aerospace "
                    "English questions."
                ),

                "metrics": [
                    "quality_score",
                    "human_acceptance",
                    "ai_human_agreement",
                    "latency",
                    "cost",
                ],
            },
        )
    )

    return protocol