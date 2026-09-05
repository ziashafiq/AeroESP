import logging
import secrets

from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


logger = logging.getLogger(__name__)

VERIFICATION_CODE_TTL_MINUTES = 10

# Backends that accept a message and never put it on the wire.
#
# locmem is deliberately absent: Django swaps it in during tests, where
# capturing into mail.outbox is exactly the intended behaviour. A
# production deployment cannot reach it by accident either, because
# config/production_check.py refuses to start without the SMTP backend.
NON_DELIVERING_BACKENDS = (
    "console.EmailBackend",
    "dummy.EmailBackend",
    "filebased.EmailBackend",
)


def _backend_can_deliver():
    return not settings.EMAIL_BACKEND.endswith(
        NON_DELIVERING_BACKENDS
    )


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

    A mail outage must not turn sign-up into a 500, so the exception is
    contained here - but it is always logged with its traceback, and
    the caller is told whether delivery actually happened. Returning
    False quietly was how a broken mail setup managed to look like a
    successful registration.
    """

    if not user.email:

        logger.error(
            "Cannot send verification code: user %s has no email address.",
            user.pk,
        )

        return False

    if not _backend_can_deliver():

        logger.error(
            "Verification code for %s was NOT delivered: EMAIL_BACKEND "
            "is %s, which does not send real mail. Set "
            "DJANGO_EMAIL_BACKEND to "
            "django.core.mail.backends.smtp.EmailBackend.",
            user.email,
            settings.EMAIL_BACKEND,
        )

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

    except Exception as error:

        # logger.exception attaches the traceback, which is what makes
        # the host's log ("Connection timed out", "Authentication
        # failed", ...) actually diagnosable after the fact.
        logger.exception(
            "FAILED to send verification code to %s via %s:%s as %s "
            "(%s). Hosting note: Render blocks outbound SMTP ports 25, "
            "465 and 587 on free web services.",
            user.email,
            settings.EMAIL_HOST,
            settings.EMAIL_PORT,
            settings.EMAIL_HOST_USER or "(no user)",
            type(error).__name__,
        )

        return False

    logger.info(
        "Verification code sent to %s via %s.",
        user.email,
        settings.EMAIL_HOST,
    )

    return True
