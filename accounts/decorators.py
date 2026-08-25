from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def student_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if hasattr(request.user, "student_profile"):
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden(
            "Student access required."
        )

    return wrapped_view


def approved_teacher_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if not hasattr(request.user, "teacher_profile"):
            raise PermissionDenied("Teacher access required.")

        if not request.user.teacher_profile.is_approved:
            return HttpResponseForbidden(
                "Teacher account is not approved."
            )

        return view_func(request, *args, **kwargs)

    return wrapped_view
