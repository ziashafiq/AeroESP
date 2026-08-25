from django.db.models import (
    Avg,
    Sum,
    Count,
)

from .models import AIInteractionEvent



def build_ai_performance():

    result = []


    providers = (
        AIInteractionEvent.objects
        .values_list(
            "provider",
            flat=True,
        )
        .distinct()
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
            }
        )


    return result