from django.db.models import (
    Avg,
    Sum,
    Count,
)

from .models import AIInteractionEvent
from .cost_estimator import (
    estimate_cost,
)


def build_ai_performance():

    result = []


    providers = sorted(
        set(
            p.strip()
            for p in
            AIInteractionEvent.objects
            .values_list(
                "provider",
                flat=True,
            )
            if p
        )
    )


    for provider in providers:

        events = (
            AIInteractionEvent.objects
            .filter(
                provider=provider,
                event_type=(
                    "GENERATION_SUCCESS"
                ),
            )
        )


        stats = events.aggregate(

            total=Count("id"),

            avg_latency=Avg(
                "latency_ms"
            ),

            avg_tokens=Avg(
                "total_tokens"
            ),

            total_tokens=Sum(
                "total_tokens"
            ),

            total_input_tokens=Sum(
                "input_tokens"
            ),

            total_output_tokens=Sum(
                "output_tokens"
            ),
        )


        estimated_cost = estimate_cost(
            provider,
            stats["total_input_tokens"] or 0,
            stats["total_output_tokens"] or 0,
        )


        result.append(
            {
                "provider": provider,

                "requests": (
                    stats["total"]
                    or 0
                ),

                "average_latency_ms": (
                    round(
                        stats[
                            "avg_latency"
                        ],
                        2,
                    )
                    if stats[
                        "avg_latency"
                    ]
                    else 0
                ),

                "average_tokens": (
                    round(
                        stats[
                            "avg_tokens"
                        ],
                        2,
                    )
                    if stats[
                        "avg_tokens"
                    ]
                    else 0
                ),

                "total_tokens": (
                    stats[
                        "total_tokens"
                    ]
                    or 0
                ),

                "estimated_cost": estimated_cost,
            }
        )


    return result