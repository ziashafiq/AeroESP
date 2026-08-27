from .models import (
    AIProviderConfiguration,
)

from .crypto import (
    encrypt_api_key,
    decrypt_api_key,
)


def save_provider_api_key(
    config,
    api_key,
):

    config.api_key = encrypt_api_key(
        api_key
    )

    config.save(
        update_fields=[
            "api_key",
        ]
    )

    return config


def get_provider_api_key(
    config,
):

    return decrypt_api_key(
        config.api_key
    )