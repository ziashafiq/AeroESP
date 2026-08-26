def build_model_recommendation(
    comparison_data,
):

    results = []


    for item in comparison_data:

        quality = (
            item.get(
                "average_quality",
                0,
            )
            or 0
        )

        acceptance = (
            item.get(
                "acceptance_rate",
                0,
            )
            or 0
        )

        generations = (
            item.get(
                "generations",
                0,
            )
            or 0
        )


        score = (
            quality * 0.5
            +
            acceptance * 0.3
            +
            min(
                generations * 2,
                20,
            )
        )


        if generations == 0:
            decision = "INSUFFICIENT_DATA"

        elif score >= 70:
            decision = "RECOMMENDED"

        elif score >= 40:
            decision = "CONSIDER"

        else:
            decision = "NOT_RECOMMENDED"


        results.append(
            {
                "provider":
                    item["provider"],

                "score":
                    round(
                        score,
                        2,
                    ),

                "decision":
                    decision,
            }
        )


    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=True,
    )