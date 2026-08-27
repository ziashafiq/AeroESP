from cryptography.fernet import (
    Fernet,
)

from django.conf import settings
from django.core.exceptions import (
    ImproperlyConfigured,
)


def get_cipher():

    key = getattr(
        settings,
        "AEROESP_SECRET_KEY",
        "",
    )

    if not key:
        raise ImproperlyConfigured(
            (
                "AEROESP_SECRET_KEY is "
                "not configured."
            )
        )

    return Fernet(
        key.encode()
    )


def encrypt_api_key(
    value,
):

    if not value:
        return ""

    return (
        get_cipher()
        .encrypt(
            value.encode()
        )
        .decode()
    )


def decrypt_api_key(
    value,
):

    if not value:
        return ""

    return (
        get_cipher()
        .decrypt(
            value.encode()
        )
        .decode()
    )