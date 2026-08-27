def normalize_provider_error(
    exc,
    provider_name,
):

    text = str(exc).lower()

    if (
        "credit_balance_exhausted" in text
        or "insufficient_quota" in text
        or "insufficient balance" in text
        or "payment required" in text
    ):
        return (
            "NO_CREDIT",
            (
                "The selected AI provider has "
                "no available API credit."
            ),
        )

    if (
        "401" in text
        or "invalid api key" in text
        or "authentication" in text
    ):
        return (
            "INVALID_API_KEY",
            (
                "The API key for the selected "
                "AI provider is invalid."
            ),
        )

    if (
        "429" in text
        or "rate limit" in text
        or "too many requests" in text
    ):
        return (
            "RATE_LIMIT",
            (
                "The selected AI provider is "
                "temporarily rate limited."
            ),
        )

    if (
        "timeout" in text
        or "timed out" in text
    ):
        return (
            "TIMEOUT",
            (
                "The AI provider did not respond "
                "within the allowed time."
            ),
        )

    if (
        "api key is missing" in text
        or "not configured" in text
        or "no api key" in text
    ):
        return (
            "API_KEY_REQUIRED",
            (
                "Configure your API key for this "
                "provider in AI Provider Settings."
            ),
        )

    if "gemini" in text and "beta" in text:
        return (
            "PROVIDER_UNAVAILABLE",
            "Gemini is not enabled in this beta.",
        )

    return (
        "PROVIDER_ERROR",
        (
            "The selected AI provider could not "
            "complete the request."
        ),
    )