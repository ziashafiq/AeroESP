PROVIDER_CONFIG = {

    "BASELINE_V1": {
        "name": "Baseline Free",
        "cost_level": "FREE",
        "requires_api_key": False,
    },

    "OPENAI_RESPONSES_V1": {
        "name": "OpenAI",
        "cost_level": "PREMIUM",
        "requires_api_key": True,
    },

    "DEEPSEEK_V1": {
        "name": "DeepSeek",
        "cost_level": "LOW",
        "requires_api_key": True,
    },

    "GEMINI_V1": {
        "name": "Gemini",
        "cost_level": "LOW",
        "requires_api_key": True,
    },

}


def get_provider_info(provider_name):

    return PROVIDER_CONFIG.get(
        provider_name,
        {},
    )


def available_providers():

    return list(
        PROVIDER_CONFIG.keys()
    )