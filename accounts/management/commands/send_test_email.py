import traceback

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        "Send a test message through the configured email backend "
        "and report exactly what went wrong if it fails."
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "recipient",
            help=(
                "Address to send the test message to. "
                "Use an inbox you can actually open."
            ),
        )

        parser.add_argument(
            "--show-config",
            action="store_true",
            help=(
                "Print the resolved email settings "
                "before sending."
            ),
        )

    # -----------------------------------------------------
    # Helpers
    # -----------------------------------------------------

    def _report_config(self):

        password = settings.EMAIL_HOST_PASSWORD

        self.stdout.write(
            "Email configuration"
        )

        self.stdout.write(
            "-------------------"
        )

        for label, value in [
            ("EMAIL_BACKEND", settings.EMAIL_BACKEND),
            ("EMAIL_HOST", settings.EMAIL_HOST or "(empty)"),
            ("EMAIL_PORT", settings.EMAIL_PORT),
            ("EMAIL_USE_TLS", settings.EMAIL_USE_TLS),
            ("EMAIL_USE_SSL", settings.EMAIL_USE_SSL),
            ("EMAIL_HOST_USER", settings.EMAIL_HOST_USER or "(empty)"),
            (
                "EMAIL_HOST_PASSWORD",
                f"set, {len(password)} chars" if password else "(empty)",
            ),
            ("DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL),
            ("EMAIL_TIMEOUT", settings.EMAIL_TIMEOUT),
        ]:

            self.stdout.write(
                f"  {label:<20} {value}"
            )

        self.stdout.write("")

    def _validate(self):
        """
        Catch the misconfigurations that produce a confusing
        'it said OK but nothing arrived' result.
        """

        backend = settings.EMAIL_BACKEND

        if backend.endswith("console.EmailBackend"):

            self.stdout.write(
                self.style.WARNING(
                    "EMAIL_BACKEND is the console backend: the message "
                    "will be printed below, NOT delivered.\n"
                    "Set DJANGO_EMAIL_BACKEND="
                    "django.core.mail.backends.smtp.EmailBackend "
                    "in your .env to send for real."
                )
            )

            return

        if backend.endswith("locmem.EmailBackend"):

            self.stdout.write(
                self.style.WARNING(
                    "EMAIL_BACKEND is the in-memory test backend: "
                    "nothing will be delivered."
                )
            )

            return

        if not backend.endswith("smtp.EmailBackend"):
            return

        problems = []

        if not settings.EMAIL_HOST:
            problems.append("DJANGO_EMAIL_HOST is empty")

        if not settings.EMAIL_HOST_USER:
            problems.append("DJANGO_EMAIL_HOST_USER is empty")

        if not settings.EMAIL_HOST_PASSWORD:
            problems.append("DJANGO_EMAIL_HOST_PASSWORD is empty")

        if settings.EMAIL_USE_TLS and settings.EMAIL_USE_SSL:
            problems.append(
                "DJANGO_EMAIL_USE_TLS and DJANGO_EMAIL_USE_SSL "
                "cannot both be 1"
            )

        if problems:

            raise CommandError(
                "Email is not configured:\n  - "
                + "\n  - ".join(problems)
            )

    def _explain(self, error):
        """
        Translate the usual SMTP failures into the actual fix.
        """

        text = f"{type(error).__name__}: {error}"

        hints = {
            "authentication": (
                "The server rejected your credentials. For Brevo the "
                "user is your SMTP login (not your account email) and "
                "the password is the generated SMTP key. For Gmail it "
                "must be a 16-character App Password, not your normal "
                "password."
            ),
            "5.7.0": (
                "Sender rejected. The DEFAULT_FROM_EMAIL address must "
                "be verified with your email provider."
            ),
            "timed out": (
                "No answer from the mail server. The host or port is "
                "wrong, or your provider blocks outbound SMTP. Many "
                "VPS providers block port 25; use 587."
            ),
            "getaddrinfo": (
                "DJANGO_EMAIL_HOST could not be resolved. Check it "
                "for typos."
            ),
            "wrong version number": (
                "TLS mismatch. Use port 587 with USE_TLS=1, or port "
                "465 with USE_SSL=1 - never both."
            ),
        }

        lowered = text.lower()

        for needle, hint in hints.items():

            if needle in lowered:
                return hint

        return None

    # -----------------------------------------------------
    # Entry point
    # -----------------------------------------------------

    def handle(self, *args, **options):

        recipient = options["recipient"]

        if options["show_config"]:
            self._report_config()

        self._validate()

        self.stdout.write(
            f"Sending test message to {recipient} ..."
        )

        message = EmailMessage(
            subject="AeroESP SMTP test",
            body=(
                "This is a test message from AeroESP.\n\n"
                "If you are reading it in your inbox, outgoing email "
                "works and account verification codes will reach "
                "your users.\n"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
        )

        try:

            sent = message.send(fail_silently=False)

        except Exception as error:

            hint = self._explain(error)

            self.stderr.write(
                self.style.ERROR(
                    f"FAILED: {type(error).__name__}: {error}"
                )
            )

            if hint:

                self.stderr.write(
                    self.style.WARNING(f"\nLikely cause: {hint}")
                )

            else:

                self.stderr.write(
                    traceback.format_exc()
                )

            raise CommandError(
                "Test email could not be sent."
            )

        if not sent:

            raise CommandError(
                "The backend reported that 0 messages were sent."
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"OK - message accepted by the server for {recipient}."
            )
        )

        self.stdout.write(
            "Check the inbox (and the spam folder) to confirm "
            "delivery."
        )
