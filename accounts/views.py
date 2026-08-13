from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import (
    approved_teacher_required,
    student_required,
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

    return render(
        request,
        "accounts/student_dashboard.html",
    )


@approved_teacher_required
def teacher_dashboard(request):

    return render(
        request,
        "accounts/teacher_dashboard.html",
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