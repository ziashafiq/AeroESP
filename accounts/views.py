import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login,
    logout,
)
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import require_POST

from .decorators import (
    approved_teacher_required,
    student_required,
)

from .forms import RegistrationForm
from .models import (
    StudentProfile,
    TeacherProfile,
    EmailVerificationCode,
)
from .utils import (
    create_verification_code,
    email_delivery_available,
    send_verification_email,
)


logger = logging.getLogger(__name__)


def error_403(request, exception=None):
    return render(request, "403.html", status=403)


def error_404(request, exception=None):
    return render(request, "404.html", status=404)


def error_500(request):
    return render(request, "500.html", status=500)


def error_400(request, exception=None):
    return render(request, "400.html", status=400)


def home(request):
    dashboard_target = None
    role = None

    if request.user.is_authenticated:
        if request.user.is_superuser:
            role = "Administrator"
            dashboard_target = "/admin/"

        elif hasattr(request.user, "teacher_profile"):
            if request.user.teacher_profile.is_approved:
                role = "Teacher"
                dashboard_target = "/learn/teacher/"
            else:
                role = "Teacher"
                dashboard_target = "/accounts/teacher/pending/"

        elif hasattr(request.user, "student_profile"):
            role = "Student"
            dashboard_target = "/learn/"

    return render(
        request,
        "accounts/home.html",
        {
            "dashboard_target": dashboard_target,
            "role": role,
        },
    )


@login_required
def role_redirect(request):

    if request.user.is_superuser:
        return redirect("/admin/")

    if hasattr(request.user, "teacher_profile"):

        if request.user.teacher_profile.is_approved:
            return redirect("accounts:teacher_dashboard")

        return redirect("accounts:teacher_pending")

    if hasattr(request.user, "student_profile"):
        return redirect("accounts:student_dashboard")

    return render(
        request,
        "accounts/no_role.html",
    )


@login_required
def account_center(request):
    """
    Universal account page for all AeroESP users.

    This is especially useful for:
    - Admin
    - Switching accounts during development/testing
    - Logout from any role
    """

    role = "No Role"

    if request.user.is_superuser:
        role = "Administrator"

    elif hasattr(request.user, "teacher_profile"):
        role = "Teacher"

    elif hasattr(request.user, "student_profile"):
        role = "Student"

    return render(
        request,
        "accounts/account_center.html",
        {
            "role": role,
        },
    )


@login_required
@require_POST
def user_logout(request):
    """
    Secure universal logout.

    Logout is performed using POST rather than a GET link.
    """

    logout(request)

    return redirect(
        "accounts:login"
    )


@student_required
def student_dashboard(request):

    return redirect(
        "learning:dashboard"
    )


@approved_teacher_required
def teacher_dashboard(request):

    return redirect(
        "learning:teacher_learning_dashboard"
    )


@login_required
def teacher_pending(request):

    if request.user.is_superuser:
        return redirect("/admin/")

    if not hasattr(
        request.user,
        "teacher_profile",
    ):
        return redirect(
            "accounts:role_redirect"
        )

    if request.user.teacher_profile.is_approved:
        return redirect(
            "accounts:teacher_dashboard"
        )

    return render(
        request,
        "accounts/teacher_pending.html",
    )


# =========================================================
# Registration / email verification
# =========================================================

PENDING_USER_SESSION_KEY = "pending_verification_user_id"

MAX_VERIFICATION_ATTEMPTS = 5


def ensure_role_profile(user):
    """
    Create the profile matching the role chosen at sign-up.
    """

    if user.selected_role == "TEACHER":
        TeacherProfile.objects.get_or_create(user=user)

    else:
        StudentProfile.objects.get_or_create(user=user)


def _log_in(request, user):
    """
    An explicit backend is required because django-axes adds a second
    authentication backend.
    """

    login(
        request,
        user,
        backend=(
            "django.contrib.auth.backends.ModelBackend"
        ),
    )


def register(request):

    if request.user.is_authenticated:

        return redirect(
            "accounts:role_redirect"
        )

    if request.method == "POST":

        form = RegistrationForm(
            request.POST
        )

        if form.is_valid():

            user = form.save(commit=False)
            user.email_verified = False
            user.is_active = True
            user.selected_role = (
                form.cleaned_data["role"]
            )

            # No mail service: finish sign-up here rather than parking
            # the account behind a code that can never be delivered.
            if not settings.REQUIRE_EMAIL_VERIFICATION:

                user.email_verified = True
                user.save()

                ensure_role_profile(user)

                _log_in(request, user)

                logger.info(
                    "Registered %s without email verification "
                    "(AEROESP_REQUIRE_EMAIL_VERIFICATION is off).",
                    user.email,
                )

                messages.success(
                    request,
                    "Welcome to AeroESP. Your account is ready. "
                    f'Your username is "{user.username}" - '
                    "you will need it (not your email) to sign in "
                    "next time.",
                )

                return redirect(
                    "accounts:role_redirect"
                )

            user.save()

            verification = (
                create_verification_code(user)
            )

            delivered = send_verification_email(
                user,
                verification.code,
            )

            # The code is only accepted for the account that is
            # pending verification in this session.
            request.session[
                PENDING_USER_SESSION_KEY
            ] = user.pk

            request.session[
                "verification_attempts"
            ] = 0

            if delivered:

                messages.success(
                    request,
                    "Your account has been created. "
                    f'Your username is "{user.username}" - '
                    "you will need it (not your email) to sign in "
                    "later. We sent a verification code to "
                    f"{user.email}.",
                )

            else:

                # Telling the user the mail is on its way when it is
                # not leaves them waiting for something that will
                # never arrive.
                messages.warning(
                    request,
                    "Your account has been created "
                    f'(username: "{user.username}"), but we could '
                    "not send the verification email. Please try "
                    "'Resend code', or contact support if the problem "
                    "continues.",
                )

            return redirect(
                "accounts:verify_email"
            )

    else:

        form = RegistrationForm()

    return render(
        request,
        "registration/register.html",
        {
            "form": form,
        },
    )


def verify_email(request):

    # The step does not exist while verification is switched off, and
    # a stale bookmark must not present a code box that can never be
    # satisfied.
    if not settings.REQUIRE_EMAIL_VERIFICATION:
        return redirect(
            "accounts:role_redirect"
            if request.user.is_authenticated
            else "accounts:login"
        )

    if request.user.is_authenticated:
        return redirect(
            "accounts:role_redirect"
        )

    user_id = request.session.get(
        PENDING_USER_SESSION_KEY
    )

    if not user_id:

        messages.error(
            request,
            "Please register or sign in first.",
        )

        return redirect(
            "accounts:register"
        )

    if request.method == "POST":

        attempts = request.session.get(
            "verification_attempts",
            0,
        )

        if attempts >= MAX_VERIFICATION_ATTEMPTS:

            request.session.pop(
                PENDING_USER_SESSION_KEY,
                None,
            )

            messages.error(
                request,
                "Too many invalid attempts. "
                "Please register again.",
            )

            return redirect(
                "accounts:register"
            )

        request.session[
            "verification_attempts"
        ] = attempts + 1

        submitted_code = (
            request.POST.get("code") or ""
        ).strip()

        verification = (
            EmailVerificationCode.objects
            .filter(
                user_id=user_id,
                code=submitted_code,
                is_used=False,
            )
            .first()
        )

        if (
            verification
            and verification.is_valid()
        ):

            user = verification.user

            user.email_verified = True
            user.save(
                update_fields=[
                    "email_verified",
                ]
            )

            ensure_role_profile(user)

            verification.is_used = True
            verification.save(
                update_fields=[
                    "is_used",
                ]
            )

            request.session.pop(
                PENDING_USER_SESSION_KEY,
                None,
            )

            request.session.pop(
                "verification_attempts",
                None,
            )

            messages.success(
                request,
                "Email verified successfully. "
                f'Your username is "{user.username}" - '
                "you will need it (not your email) to sign in "
                "next time.",
            )

            _log_in(request, user)

            return redirect(
                "accounts:role_redirect"
            )

        messages.error(
            request,
            "Invalid or expired verification code.",
        )

    return render(
        request,
        "registration/verify_email.html",
    )


@require_POST
def resend_verification_code(request):

    if not settings.REQUIRE_EMAIL_VERIFICATION:
        return redirect(
            "accounts:login"
        )

    user_id = request.session.get(
        PENDING_USER_SESSION_KEY
    )

    if not user_id:
        return redirect(
            "accounts:register"
        )

    user = get_object_or_404(
        get_user_model(),
        pk=user_id,
        email_verified=False,
    )

    verification = create_verification_code(user)

    delivered = send_verification_email(
        user,
        verification.code,
    )

    request.session[
        "verification_attempts"
    ] = 0

    if delivered:

        messages.success(
            request,
            "A new verification code has been sent.",
        )

    else:

        messages.error(
            request,
            "We could not send the verification email. "
            "Please contact support.",
        )

    return redirect(
        "accounts:verify_email"
    )

# =========================================================
# Password reset
# =========================================================

class LoudPasswordResetForm(PasswordResetForm):
    """
    Let a failed send be noticed.

    Django's PasswordResetForm.send_mail swallows every exception and
    only logs it, so a broken mail service still redirects the visitor
    to "check your email" for a message that was never sent. This
    rebuilds the message exactly as Django does and lets the error
    propagate, so the view can say something true instead.
    """

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):

        subject = "".join(
            loader.render_to_string(
                subject_template_name,
                context,
            ).splitlines()
        )

        body = loader.render_to_string(
            email_template_name,
            context,
        )

        message = EmailMultiAlternatives(
            subject,
            body,
            from_email,
            [to_email],
        )

        if html_email_template_name is not None:
            message.attach_alternative(
                loader.render_to_string(
                    html_email_template_name,
                    context,
                ),
                "text/html",
            )

        message.send(fail_silently=False)


class PasswordResetOrSupportView(auth_views.PasswordResetView):
    """
    Django's PasswordResetView always reports success, so that an
    attacker cannot learn which addresses are registered. That is the
    right behaviour, but it means a mail failure surfaces as a 500 -
    or, worse, as a cheerful "check your inbox" for a message that was
    never sent.

    When the backend cannot deliver at all, or the send raises, an
    explanatory page is shown instead.
    """

    form_class = LoudPasswordResetForm

    template_name = (
        "registration/password_reset_form.html"
    )

    email_template_name = (
        "registration/password_reset_email.txt"
    )

    subject_template_name = (
        "registration/password_reset_subject.txt"
    )

    def _unavailable(self, request):

        return render(
            request,
            "registration/password_reset_unavailable.html",
            {
                "support_email": (
                    settings.AEROESP_SUPPORT_EMAIL
                ),
            },
            status=503,
        )

    def dispatch(self, request, *args, **kwargs):

        if not email_delivery_available():

            logger.warning(
                "Password reset requested while EMAIL_BACKEND is %s, "
                "which cannot deliver; showing the unavailable page.",
                settings.EMAIL_BACKEND,
            )

            return self._unavailable(request)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):

        try:
            return super().form_valid(form)

        except Exception:

            logger.exception(
                "Password reset email could not be sent via %s:%s.",
                settings.EMAIL_HOST,
                settings.EMAIL_PORT,
            )

            return self._unavailable(self.request)
