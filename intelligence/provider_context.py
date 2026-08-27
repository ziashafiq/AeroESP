from .models import (
    AIProviderConfiguration,
)

from .provider_service import (
    get_provider_api_key,
)


def get_user_provider_config(
    user,
    provider_name=None,
):

    queryset = (
        AIProviderConfiguration.objects
        .filter(
            user=user,
            is_active=True,
        )
    )

    if provider_name:
        queryset = queryset.filter(
            provider_name=provider_name
        )

    return (
        queryset
        .order_by("-updated_at")
        .first()
    )


def get_user_provider_key(
    user,
    provider_name=None,
):

    config = get_user_provider_config(
        user,
        provider_name,
    )

    if not config:
        return None

    return get_provider_api_key(
        config
    )


def get_active_user_provider(
    user,
    provider_name=None,
):
    """
    Returns the active provider configuration for the user as a dictionary.
    If no active configuration exists, returns None.

    Args:
        user: User instance
        provider_name: Optional provider name to filter

    Returns:
        dict or None: {
            "provider_name": str,
            "model_name": str,
            "api_key": str  # decrypted API key
        }
    """
    config = get_user_provider_config(
        user,
        provider_name,
    )

    if not config:
        return None

    return {
        "provider_name": config.provider_name,
        "model_name": config.model_name,
        "api_key": get_provider_api_key(config),
    }