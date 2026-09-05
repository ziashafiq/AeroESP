import os


os.environ["DJANGO_ENV"] = "development"

os.environ["DJANGO_DEBUG"] = "0"

os.environ["DJANGO_SECRET_KEY"] = (
    "aeroesp-test-only-django-secret-key-"
    "not-for-production-2026-abcdef123456789"
)

os.environ["AEROESP_SECRET_KEY"] = (
    "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA="
)


from .settings import *


DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.sqlite3"
        ),
        "NAME": ":memory:",
    }
}


PASSWORD_HASHERS = [
    (
        "django.contrib.auth.hashers."
        "MD5PasswordHasher"
    ),
]


EMAIL_BACKEND = (
    "django.core.mail.backends.locmem."
    "EmailBackend"
)


DEBUG = False


# django-axes would lock out the shared test client after a handful
# of deliberate bad-credential assertions.
AXES_ENABLED = False


SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0

SECURE_HSTS_INCLUDE_SUBDOMAINS = False

SECURE_HSTS_PRELOAD = False