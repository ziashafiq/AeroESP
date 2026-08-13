from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

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

    if not hasattr(request.user, "teacher_profile"):
        return redirect("accounts:role_redirect")

    if request.user.teacher_profile.is_approved:
        return redirect("accounts:teacher_dashboard")

    return render(
        request,
        "accounts/teacher_pending.html",
    )