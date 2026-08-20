from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from assessment.models import Question

from learning.models import Enrollment

from .models import (
    LearnerInsightSnapshot,
    QuestionAISuggestion,
)

from .services import (
    analyze_question,
    build_learner_insight,
)


def _require_teacher(user):

    if user.is_superuser:
        return

    profile = getattr(
        user,
        "teacher_profile",
        None,
    )

    if (
        profile is None
        or not profile.is_approved
    ):
        raise PermissionDenied(
            "Approved teacher access required."
        )


@login_required
def ai_dashboard(request):

    _require_teacher(
        request.user
    )

    suggestions = (
        QuestionAISuggestion.objects
        .select_related(
            "question",
            "suggested_domain",
            "suggested_topic",
        )
    )

    insights = (
        LearnerInsightSnapshot.objects
        .select_related("student")
    )

    if not request.user.is_superuser:

        suggestions = (
            suggestions.filter(
                created_by=request.user
            )
        )

        insights = (
            insights.filter(
                student__learning_enrollments__course__created_by=request.user
            )
            .distinct()
        )

    suggestions = (
        suggestions
        .order_by("-created_at")[:30]
    )

    insights = (
        insights
        .order_by("-generated_at")[:30]
    )

    return render(
        request,
        "intelligence/dashboard.html",
        {
            "suggestions": suggestions,
            "insights": insights,
        },
    )


@login_required
def analyze_question_view(
    request,
    question_id,
):

    _require_teacher(
        request.user
    )

    question = get_object_or_404(
        Question,
        pk=question_id,
    )

    if request.method == "POST":

        suggestion = analyze_question(
            question,
            created_by=request.user,
        )

        return redirect(
            "intelligence:suggestion_detail",
            suggestion_id=suggestion.pk,
        )

    return render(
        request,
        "intelligence/analyze_question.html",
        {
            "question": question,
        },
    )


@login_required
def suggestion_detail(
    request,
    suggestion_id,
):

    _require_teacher(
        request.user
    )

    suggestions = (
        QuestionAISuggestion.objects
        .select_related(
            "question",
            "suggested_domain",
            "suggested_topic",
        )
    )

    if not request.user.is_superuser:

        suggestions = (
            suggestions.filter(
                created_by=request.user
            )
        )

    suggestion = get_object_or_404(
        suggestions,
        pk=suggestion_id,
    )

    return render(
        request,
        "intelligence/suggestion_detail.html",
        {
            "suggestion": suggestion,
        },
    )


@login_required
def review_suggestion(
    request,
    suggestion_id,
    decision,
):

    _require_teacher(
        request.user
    )

    if request.method != "POST":
        raise PermissionDenied()

    suggestions = (
        QuestionAISuggestion.objects.all()
    )

    if not request.user.is_superuser:

        suggestions = (
            suggestions.filter(
                created_by=request.user
            )
        )

    suggestion = get_object_or_404(
        suggestions,
        pk=suggestion_id,
    )

    if decision == "accept":

        suggestion.status = (
            QuestionAISuggestion
            .Status
            .ACCEPTED
        )

    elif decision == "reject":

        suggestion.status = (
            QuestionAISuggestion
            .Status
            .REJECTED
        )

    else:

        raise PermissionDenied()

    suggestion.reviewed_by = (
        request.user
    )

    suggestion.reviewed_at = (
        timezone.now()
    )

    suggestion.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    return redirect(
        "intelligence:suggestion_detail",
        suggestion_id=suggestion.pk,
    )


@login_required
def learner_insight(
    request,
    student_id,
):

    _require_teacher(
        request.user
    )

    enrollments = (
        Enrollment.objects
        .filter(
            student_id=student_id,
        )
        .select_related(
            "student",
            "course",
        )
    )

    if not request.user.is_superuser:

        enrollments = (
            enrollments.filter(
                course__created_by=request.user
            )
        )

    enrollment = (
        enrollments.first()
    )

    if enrollment is None:

        raise PermissionDenied(
            "This learner is not enrolled "
            "in one of your courses."
        )

    student = (
        enrollment.student
    )

    scope = (
        request.GET.get(
            "scope",
            "OVERALL",
        )
        .strip()
        .upper()
    )

    if scope not in {
        "OVERALL",
        "GENERAL",
        "AEROSPACE",
    }:

        scope = "OVERALL"

    snapshot = (
        build_learner_insight(
            student,
            scope,
        )
    )

    return render(
        request,
        "intelligence/learner_insight.html",
        {
            "student_object": student,
            "snapshot": snapshot,
        },
    )