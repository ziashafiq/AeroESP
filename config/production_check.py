import os
import sys

from cryptography.fernet import Fernet


REQUIRED = [
    "DJANGO_SECRET_KEY",
    "DJANGO_ALLOWED_HOSTS",
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "AEROESP_SECRET_KEY",
    "AEROESP_DB_NAME",
    "AEROESP_DB_USER",
    "AEROESP_DB_PASSWORD",
    "AEROESP_DB_HOST",
]


def main():

    errors = []

    for name in REQUIRED:

        if not os.getenv(
            name,
            "",
        ).strip():

            errors.append(
                f"MISSING: {name}"
            )

    environment = os.getenv(
        "DJANGO_ENV",
        "",
    ).strip().lower()

    if environment != "production":

        errors.append(
            "DJANGO_ENV must be production."
        )

    debug_value = os.getenv(
        "DJANGO_DEBUG",
        "",
    ).strip().lower()

    if debug_value not in {
        "0",
        "false",
        "no",
        "off",
    }:

        errors.append(
            "DJANGO_DEBUG must be disabled."
        )

    django_secret = os.getenv(
        "DJANGO_SECRET_KEY",
        "",
    )

    if (
        django_secret
        and len(django_secret) < 50
    ):

        errors.append(
            (
                "DJANGO_SECRET_KEY must contain "
                "at least 50 characters."
            )
        )

    aeroesp_secret = os.getenv(
        "AEROESP_SECRET_KEY",
        "",
    )

    if aeroesp_secret:

        try:

            Fernet(
                aeroesp_secret.encode()
            )

        except Exception:

            errors.append(
                (
                    "AEROESP_SECRET_KEY is not "
                    "a valid Fernet key."
                )
            )

    # Account verification codes are delivered by email, so a
    # non-sending backend means nobody can finish signing up.

    email_backend = os.getenv(
        "DJANGO_EMAIL_BACKEND",
        "",
    ).strip()

    if not email_backend.endswith(
        "smtp.EmailBackend"
    ):

        errors.append(
            (
                "DJANGO_EMAIL_BACKEND must be "
                "django.core.mail.backends.smtp.EmailBackend "
                "in production; verification codes cannot be "
                "delivered otherwise."
            )
        )

    else:

        for name in [
            "DJANGO_EMAIL_HOST",
            "DJANGO_EMAIL_HOST_USER",
            "DJANGO_EMAIL_HOST_PASSWORD",
            "DJANGO_DEFAULT_FROM_EMAIL",
        ]:

            if not os.getenv(
                name,
                "",
            ).strip():

                errors.append(
                    f"MISSING: {name} (required for SMTP email)"
                )

        if (
            os.getenv("DJANGO_EMAIL_USE_TLS", "") == "1"
            and os.getenv("DJANGO_EMAIL_USE_SSL", "") == "1"
        ):

            errors.append(
                (
                    "DJANGO_EMAIL_USE_TLS and "
                    "DJANGO_EMAIL_USE_SSL cannot both be 1."
                )
            )

    if errors:

        print(
            "PRODUCTION CHECK: FAILED"
        )

        for error in errors:

            print(error)

        sys.exit(1)

    print(
        "PRODUCTION CHECK: OK"
    )


if __name__ == "__main__":
    main()