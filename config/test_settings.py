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


SECURE_SSL_REDIRECT = False

SESSION_COOKIE_SECURE = False

CSRF_COOKIE_SECURE = False

SECURE_HSTS_SECONDS = 0