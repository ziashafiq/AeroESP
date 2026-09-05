import secrets

from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


VERIFICATION_CODE_TTL_MINUTES = 10


def generate_verification_code():
    """
    Six digit code from a cryptographically secure source.

    random.randint() is predictable and must not be used for
    anything that grants account access.
    """

    return f"{secrets.randbelow(1000000):06d}"


def create_verification_code(user):
    """
    Invalidate any outstanding codes for the user and issue a new one.
    """

    from .models import EmailVerificationCode

    EmailVerificationCode.objects.filter(
        user=user,
        is_used=False,
    ).update(
        is_used=True,
    )

    return EmailVerificationCode.objects.create(
        user=user,
        code=generate_verification_code(),
        expires_at=(
            timezone.now()
            + timedelta(
                minutes=VERIFICATION_CODE_TTL_MINUTES,
            )
        ),
    )


def send_verification_email(user, code):
    """
    Deliver the verification code.

    Errors are swallowed on purpose: a mail outage must not turn
    sign-up into a 500. The user can always request a new code.
    """

    if not user.email:
        return False

    try:
        send_mail(
            subject="Your AeroESP verification code",
            message=(
                f"Hello {user.first_name or user.username},\n\n"
                f"Your AeroESP verification code is: {code}\n\n"
                f"It expires in "
                f"{VERIFICATION_CODE_TTL_MINUTES} minutes.\n\n"
                "If you did not create an AeroESP account, "
                "you can ignore this message.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    except Exception:
        return False

    return True
