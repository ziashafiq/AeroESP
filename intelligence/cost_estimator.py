from decimal import Decimal


# Approximate token prices
# Can be updated when provider pricing changes

PRICING = {

    "OPENAI_RESPONSES_V1": {

        "input": Decimal("0.000005"),

        "output": Decimal("0.000015"),
    },


    "BASELINE_V1": {

        "input": Decimal("0"),

        "output": Decimal("0"),
    },

}



def estimate_cost(
    provider,
    input_tokens=0,
    output_tokens=0,
):

    price = PRICING.get(
        provider,
        PRICING["BASELINE_V1"],
    )


    input_cost = (
        Decimal(
            input_tokens or 0
        )
        *
        price["input"]
    )


    output_cost = (
        Decimal(
            output_tokens or 0
        )
        *
        price["output"]
    )


    return round(
        input_cost + output_cost,
        8,
    )