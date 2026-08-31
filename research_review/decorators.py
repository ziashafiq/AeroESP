from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def expert_reviewer_required(view_func):
    """
    Allow access only to active expert reviewers.
    """

    @wraps(view_func)
    @login_required
    def wrapped_view(request, *args, **kwargs):

        profile = getattr(
            request.user,
            "expert_reviewer_profile",
            None,
        )

        if profile is None:
            raise PermissionDenied(
                "Expert reviewer access required."
            )

        if not profile.is_active_reviewer:
            raise PermissionDenied(
                "Expert reviewer account is inactive."
            )

        request.expert_reviewer = profile

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapped_view