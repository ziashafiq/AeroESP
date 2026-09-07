from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .models import HelpGuide


def relevant_audiences(user):
    """
    Which HelpGuide.Audience values apply to this user, most specific
    (most useful) first.

    An approved teacher who is also an active expert reviewer sees the
    reviewer guide before the general teacher one.
    """

    if not user.is_authenticated:
        return []

    audiences = []

    reviewer_profile = getattr(
        user,
        "expert_reviewer_profile",
        None,
    )

    if reviewer_profile and reviewer_profile.is_active_reviewer:
        audiences.append(HelpGuide.Audience.EXPERT_REVIEWER)

    if hasattr(user, "teacher_profile"):
        audiences.append(HelpGuide.Audience.TEACHER)

    if hasattr(user, "student_profile"):
        audiences.append(HelpGuide.Audience.STUDENT)

    return audiences


def help_list(request):
    """
    Every published guide, grouped by audience.

    Public on purpose: a prospective teacher or reviewer needs to read
    the relevant guide before they have an account at all.
    """

    guides = HelpGuide.objects.filter(
        is_published=True,
    )

    requested = request.GET.get(
        "audience",
        "",
    ).upper()

    highlighted_audience = (
        requested
        if requested in HelpGuide.Audience.values
        else ""
    )

    return render(
        request,
        "accounts/help_list.html",
        {
            "guides": guides,
            "highlighted_audience": highlighted_audience,
            "support_email": settings.AEROESP_SUPPORT_EMAIL,
        },
    )


def help_detail(request, slug):

    guide = get_object_or_404(
        HelpGuide,
        slug=slug,
        is_published=True,
    )

    return render(
        request,
        "accounts/help_detail.html",
        {
            "guide": guide,
        },
    )


def help_for_me(request):
    """
    The topbar Help icon's target: jump to the guide list pre-filtered
    to whichever role is most relevant to the signed-in user.
    """

    audiences = relevant_audiences(request.user)

    if not audiences:
        return redirect("help_list")

    return redirect(
        f"{reverse('help_list')}?audience={audiences[0]}"
    )
