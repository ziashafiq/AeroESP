from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import (
    approved_teacher_required,
    student_required,
)

from django.shortcuts import render

def error_403(request, exception=None):
    return render(request, "403.html", status=403)

def error_404(request, exception=None):
    return render(request, "404.html", status=404)

def error_500(request):
    return render(request, "500.html", status=500)

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
# UI-08 Public Error Pages
# =========================================================

def error_403(
    request,
    exception=None,
):
    return render(
        request,
        "403.html",
        status=403,
    )


def error_404(
    request,
    exception=None,
):
    return render(
        request,
        "404.html",
        status=404,
    )


def error_500(
    request,
):
    return render(
        request,
        "500.html",
        status=500,
    )
def error_400(
    request,
    exception=None,
):

    return render(
        request,
        "400.html",
        status=400,
    )