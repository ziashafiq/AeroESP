from .model_comparison import (
    build_model_comparison,
)


def select_best_provider():

    comparison = build_model_comparison()

    if not comparison:
        return "BASELINE_V1"


    recommended = sorted(
        comparison,
        key=lambda x: (
            x.get(
                "average_quality",
                0,
            ),
            x.get(
                "acceptance_rate",
                0,
            ),
        ),
        reverse=True,
    )


    return recommended[0]["provider"]