from django.contrib import messages
from django.contrib.auth import (
    get_user_model,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required
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
    send_verification_email,
)


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
                    "We sent a verification code to "
                    f"{user.email}.",
                )

            else:

                # Telling the user the mail is on its way when it is
                # not leaves them waiting for something that will
                # never arrive.
                messages.warning(
                    request,
                    "Your account has been created, but we could not "
                    "send the verification email. Please try "
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

            if user.selected_role == "TEACHER":
                TeacherProfile.objects.get_or_create(
                    user=user
                )
            else:
                StudentProfile.objects.get_or_create(
                    user=user
                )

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
                "Email verified successfully.",
            )

            # An explicit backend is required because more than one
            # authentication backend is configured (django-axes).
            login(
                request,
                user,
                backend=(
                    "django.contrib.auth.backends."
                    "ModelBackend"
                ),
            )

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