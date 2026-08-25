from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from assessment.forms import TeacherQuestionForm
from assessment.models import Question

from learning.models import Enrollment
from .quality import evaluate_question_quality
from .quality_advisor import build_quality_advice
from .forms import QuestionGenerationForm
from .models import (
    GeneratedQuestionDraft,
    AIInteractionEvent,
    AIQualitySnapshot,
    LearnerInsightSnapshot,
    QuestionAISuggestion,
)
from .services import (
    QuestionGenerationError,
    analyze_question,
    build_learner_insight,
    get_question_generator,
)
from .feedback import (
    build_ai_feedback_summary,
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

    from django.db.models import Count, Q

    ai_events = AIInteractionEvent.objects.all()

    if not request.user.is_superuser:
        ai_events = ai_events.filter(
            actor=request.user
        )

    ai_stats = {
        "total_events": ai_events.count(),

        "success_events": ai_events.filter(
            event_type="GENERATION_SUCCESS"
        ).count(),

        "failure_events": ai_events.filter(
            event_type="GENERATION_FAILURE"
        ).count(),

        "drafts_pending": GeneratedQuestionDraft.objects.filter(
            status="PENDING"
        ).count(),

        "drafts_accepted": GeneratedQuestionDraft.objects.filter(
            status="ACCEPTED"
        ).count(),

        "drafts_rejected": GeneratedQuestionDraft.objects.filter(
            status="REJECTED"
        ).count(),

        "quality_good": GeneratedQuestionDraft.objects.filter(
            generation_metadata__quality__status="GOOD"
        ).count(),

        "quality_review": GeneratedQuestionDraft.objects.filter(
            generation_metadata__quality__status="REVIEW"
        ).count(),

        "quality_poor": GeneratedQuestionDraft.objects.filter(
            generation_metadata__quality__status="POOR"
        ).count(),

        "acceptance_rate": 0,

        "edit_rate": 0,

        "rejection_rate": 0,

        "average_quality_score": 0,
    }

    # Compute additional statistics
    total_reviewed = (
        GeneratedQuestionDraft.objects
        .filter(
            status__in=[
                "ACCEPTED",
                "REJECTED",
            ]
        )
        .count()
    )

    accepted_count = (
        GeneratedQuestionDraft.objects
        .filter(
            status="ACCEPTED"
        )
        .count()
    )

    rejected_count = (
        GeneratedQuestionDraft.objects
        .filter(
            status="REJECTED"
        )
        .count()
    )

    edited_count = (
        AIInteractionEvent.objects
        .filter(
            event_type="DRAFT_EDITED"
        )
        .count()
    )

    snapshots = (
        AIQualitySnapshot.objects
        .all()
    )

    if total_reviewed:

        ai_stats["acceptance_rate"] = round(
            accepted_count
            /
            total_reviewed
            *
            100,
            2,
        )

        ai_stats["rejection_rate"] = round(
            rejected_count
            /
            total_reviewed
            *
            100,
            2,
        )

    if ai_events.count():

        ai_stats["edit_rate"] = round(
            edited_count
            /
            ai_events.count()
            *
            100,
            2,
        )

    if snapshots.exists():

        ai_stats["average_quality_score"] = round(
            sum(
                s.score
                for s in snapshots
            )
            /
            snapshots.count(),
            2,
        )

    provider_stats = []

    for row in (
        ai_events
        .values("provider")
        .annotate(total=Count("id"))
        .order_by("-total")
    ):
        provider_events = ai_events.filter(
            provider=row["provider"]
        )

        provider_stats.append(
            {
                "provider": row["provider"],
                "total": row["total"],
                "success": provider_events.filter(
                    success=True
                ).count(),
                "failure": provider_events.filter(
                    success=False
                ).count(),
            }
        )

    recent_ai_events = (
        ai_events
        .select_related("actor", "draft")
        .order_by("-created_at")[:10]
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
            "ai_stats": ai_stats,
            "provider_stats": provider_stats,
            "recent_ai_events": recent_ai_events,
            "feedback_summary": (
                build_ai_feedback_summary()
            ),
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


# =========================================================
# AI Question Generation Views
# =========================================================

@login_required
def generate_question_view(request):

    _require_teacher(request.user)

    if request.method == "POST":

        form = QuestionGenerationForm(
            request.POST,
        )

        if form.is_valid():

            data = form.cleaned_data

            try:
                provider_name = data.get("provider", "BASELINE_V1")
                generator = get_question_generator(provider_name)
                result = generator.generate(
                    track=data["track"],
                    skill=data["skill"],
                    difficulty=data["difficulty"],
                    domain=data.get("domain"),
                    topic=data.get("topic"),
                    theme=data.get("theme", ""),
                    teacher_instructions=(
                        data.get(
                            "teacher_instructions",
                            "",
                        )
                    ),
                )
                quality_report = evaluate_question_quality(
                    result=result,
                    track=data["track"],
                    skill=data["skill"],
                    difficulty=data["difficulty"],
                )


                result["metadata"]["quality"] = quality_report

                result["metadata"]["quality_advice"] = (
                    build_quality_advice(
                        quality_report
                    )
                )
                draft = (
                    GeneratedQuestionDraft
                    .objects
                    .create(
                        created_by=request.user,
                        track=data["track"],
                        skill=data["skill"],
                        difficulty=data[
                            "difficulty"
                        ],
                        domain=data.get(
                            "domain"
                        ),
                        topic=data.get(
                            "topic"
                        ),
                        theme=data.get(
                            "theme",
                            "",
                        ),
                        teacher_instructions=(
                            data.get(
                                "teacher_instructions",
                                "",
                            )
                        ),
                        question_text=result[
                            "question_text"
                        ],
                        option_a=result[
                            "option_a"
                        ],
                        option_b=result[
                            "option_b"
                        ],
                        option_c=result[
                            "option_c"
                        ],
                        option_d=result[
                            "option_d"
                        ],
                        correct_answer=result[
                            "correct_answer"
                        ],
                        explanation=result[
                            "explanation"
                        ],
                        provider=result[
                            "provider"
                        ],
                        generation_metadata=(
                            result["metadata"]
                        ),
                    )
                )

                success_event = AIInteractionEvent.objects.create(
                    actor=request.user,
                    draft=draft,
                    event_type="GENERATION_SUCCESS",
                    provider=result.get(
                        "provider",
                        provider_name,
                    ),
                    model_name=result.get(
                        "metadata",
                        {},
                    ).get(
                        "model",
                        "",
                    ),

                    latency_ms=result.get(
                        "metadata",
                        {},
                    ).get(
                        "latency_ms",
                        0,
                    ),

                    input_tokens=result.get(
                        "metadata",
                        {},
                    ).get(
                        "input_tokens",
                        0,
                    ),

                    output_tokens=result.get(
                        "metadata",
                        {},
                    ).get(
                        "output_tokens",
                        0,
                    ),

                    total_tokens=result.get(
                        "metadata",
                        {},
                    ).get(
                        "total_tokens",
                        0,
                    ),

                    request_id=result.get(
                        "metadata",
                        {},
                    ).get(
                        "request_id",
                        "",
                    ),

                    prompt_version=result.get(
                        "metadata",
                        {},
                    ).get(
                        "prompt_version",
                        "",
                    ),

                    success=True,
                    metadata={
                        "track": str(
                            data["track"]
                        ),
                        "skill": str(
                            data["skill"]
                        ),
                        "difficulty": str(
                            data["difficulty"]
                        ),
                    },
                )

                AIQualitySnapshot.objects.create(
                    draft=draft,
                    event=success_event,
                    score=result["metadata"]["quality"]["score"],
                    status=result["metadata"]["quality"]["status"],
                    decision=result["metadata"]["quality_advice"]["decision"],
                    quality_data={
                        "quality": result["metadata"]["quality"],
                        "advice": result["metadata"]["quality_advice"],
                    },
                )

                return redirect(
                    "intelligence:"
                    "generated_draft_detail",
                    draft_id=draft.pk,
                )

            except QuestionGenerationError as exc:

                AIInteractionEvent.objects.create(
                    actor=request.user,
                    event_type="GENERATION_FAILURE",
                    provider=provider_name,
                    success=False,
                    metadata={
                        "error": str(exc),
                        "track": str(
                            data.get("track")
                        ),
                        "skill": str(
                            data.get("skill")
                        ),
                        "difficulty": str(
                            data.get("difficulty")
                        ),
                    },
                )

                form.add_error(
                    None,
                    str(exc),
                )

    else:

        form = (
            QuestionGenerationForm()
        )

    return render(
        request,
        (
            "intelligence/"
            "generate_question.html"
        ),
        {
            "form": form,
        },
    )


@login_required
def generated_draft_detail(
    request,
    draft_id,
):

    _require_teacher(
        request.user
    )

    drafts = (
        GeneratedQuestionDraft
        .objects
        .select_related(
            "domain",
            "topic",
            "created_question",
        )
    )

    if not request.user.is_superuser:
        drafts = drafts.filter(
            created_by=request.user
        )

    draft = get_object_or_404(
        drafts,
        pk=draft_id,
    )

    return render(
        request,
        (
            "intelligence/"
            "generated_draft_detail.html"
        ),
        {
            "draft": draft,
            "quality_history": (
                draft
                .quality_snapshots
                .all()
            ),
        },
    )


@login_required
def edit_generated_draft(
    request,
    draft_id,
):

    _require_teacher(
        request.user
    )

    drafts = (
        GeneratedQuestionDraft
        .objects
        .filter(
            status=(
                GeneratedQuestionDraft
                .Status
                .PENDING
            )
        )
    )

    if not request.user.is_superuser:
        drafts = drafts.filter(
            created_by=request.user
        )

    draft = get_object_or_404(
        drafts,
        pk=draft_id,
    )

    if request.method == "POST":

        fields = [
            "question_text",
            "option_a",
            "option_b",
            "option_c",
            "option_d",
            "correct_answer",
            "explanation",
        ]

        for field in fields:

            value = (
                request.POST.get(
                    field,
                    "",
                )
                .strip()
            )

            setattr(
                draft,
                field,
                value,
            )

        if draft.correct_answer not in {
            "A",
            "B",
            "C",
            "D",
        }:

            return render(
                request,
                (
                    "intelligence/"
                    "edit_generated_draft.html"
                ),
                {
                    "draft": draft,
                    "error_message": (
                        "Correct answer must "
                        "be A, B, C, or D."
                    ),
                },
            )

        draft.save()

        edit_event = AIInteractionEvent.objects.create(
            actor=request.user,
            draft=draft,
            event_type="DRAFT_EDITED",
            provider=draft.provider,
            success=True,
            metadata={
                "action": "teacher_edit",
                "fields": fields,
            },
        )

        AIQualitySnapshot.objects.create(
            draft=draft,
            event=edit_event,
            score=draft.generation_metadata.get(
                "quality",
                {},
            ).get(
                "score",
                0,
            ),
            status=draft.generation_metadata.get(
                "quality",
                {},
            ).get(
                "status",
                "",
            ),
            decision=draft.generation_metadata.get(
                "quality_advice",
                {},
            ).get(
                "decision",
                "",
            ),
            quality_data={
                "action": "teacher_edit",
                "quality": draft.generation_metadata.get(
                    "quality",
                    {},
                ),
                "advice": draft.generation_metadata.get(
                    "quality_advice",
                    {},
                ),
            },
        )

        return redirect(
            "intelligence:"
            "generated_draft_detail",
            draft_id=draft.pk,
        )

    return render(
        request,
        (
            "intelligence/"
            "edit_generated_draft.html"
        ),
        {
            "draft": draft,
        },
    )


@login_required
def accept_generated_draft(
    request,
    draft_id,
):

    _require_teacher(
        request.user
    )

    if request.method != "POST":
        raise PermissionDenied()

    drafts = (
        GeneratedQuestionDraft
        .objects
        .filter(
            status=(
                GeneratedQuestionDraft
                .Status
                .PENDING
            )
        )
    )

    if not request.user.is_superuser:
        drafts = drafts.filter(
            created_by=request.user
        )

    draft = get_object_or_404(
        drafts,
        pk=draft_id,
    )

    # Prepare form data for TeacherQuestionForm
    form_data = {
        "question_text": draft.question_text,
        "option_a": draft.option_a,
        "option_b": draft.option_b,
        "option_c": draft.option_c,
        "option_d": draft.option_d,
        "correct_answer": draft.correct_answer,
        "explanation": draft.explanation,
        "question_language": Question.Language.ENGLISH,
        "options_language": Question.Language.ENGLISH,
        "skill": draft.skill,
        "track": draft.track,
        "domain_ref": (
            draft.domain_id
            if draft.domain_id
            else ""
        ),
        "topic_ref": (
            draft.topic_id
            if draft.topic_id
            else ""
        ),
        "difficulty": (
            draft.difficulty
        ),
        "source_reference": (
            "AI-assisted draft; "
            f"provider={draft.provider}; "
            f"draft_id={draft.pk}"
        ),
        "visibility": (
            Question.Visibility.PRIVATE
        ),
    }

    form = TeacherQuestionForm(
        data=form_data
    )

    if not form.is_valid():

        return render(
            request,
            (
                "intelligence/"
                "generated_draft_detail.html"
            ),
            {
                "draft": draft,
                "question_form_errors": (
                    form.errors
                ),
            },
        )

    question = form.save(
        commit=False
    )

    question.owner = (
        request.user
    )

    question.source_type = (
        Question.SourceType.AI
    )

    question.status = (
        Question.Status.DRAFT
    )

    question.visibility = (
        Question.Visibility.PRIVATE
    )

    question.full_clean()
    question.save()

    draft.status = (
        GeneratedQuestionDraft
        .Status
        .ACCEPTED
    )

    draft.created_question = (
        question
    )

    draft.reviewed_by = (
        request.user
    )

    draft.reviewed_at = (
        timezone.now()
    )

    draft.save(
        update_fields=[
            "status",
            "created_question",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    accept_event = AIInteractionEvent.objects.create(
        actor=request.user,
        draft=draft,
        question=question,
        event_type="DRAFT_ACCEPTED",
        provider=draft.provider,
        success=True,
        metadata={
            "action": "accepted_to_question_bank",
        },
    )

    AIQualitySnapshot.objects.create(
        draft=draft,
        event=accept_event,
        score=draft.generation_metadata.get(
            "quality",
            {},
        ).get(
            "score",
            0,
        ),
        status=draft.generation_metadata.get(
            "quality",
            {},
        ).get(
            "status",
            "",
        ),
        decision=draft.generation_metadata.get(
            "quality_advice",
            {},
        ).get(
            "decision",
            "",
        ),
        quality_data={
            "action": "teacher_accept",
            "quality": draft.generation_metadata.get(
                "quality",
                {},
            ),
            "advice": draft.generation_metadata.get(
                "quality_advice",
                {},
            ),
        },
    )

    return redirect(
        "intelligence:"
        "generated_draft_detail",
        draft_id=draft.pk,
    )


@login_required
def reject_generated_draft(
    request,
    draft_id,
):

    _require_teacher(
        request.user
    )

    if request.method != "POST":
        raise PermissionDenied()

    drafts = (
        GeneratedQuestionDraft
        .objects
        .filter(
            status=(
                GeneratedQuestionDraft
                .Status
                .PENDING
            )
        )
    )

    if not request.user.is_superuser:
        drafts = drafts.filter(
            created_by=request.user
        )

    draft = get_object_or_404(
        drafts,
        pk=draft_id,
    )

    draft.status = (
        GeneratedQuestionDraft
        .Status
        .REJECTED
    )

    draft.reviewed_by = (
        request.user
    )

    draft.reviewed_at = (
        timezone.now()
    )

    draft.save(
        update_fields=[
            "status",
            "reviewed_by",
            "reviewed_at",
        ]
    )

    reject_event = AIInteractionEvent.objects.create(
        actor=request.user,
        draft=draft,
        event_type="DRAFT_REJECTED",
        provider=draft.provider,
        success=True,
        metadata={
            "action": "rejected_by_teacher",
        },
    )

    AIQualitySnapshot.objects.create(
        draft=draft,
        event=reject_event,
        score=draft.generation_metadata.get(
            "quality",
            {},
        ).get(
            "score",
            0,
        ),
        status=draft.generation_metadata.get(
            "quality",
            {},
        ).get(
            "status",
            "",
        ),
        decision=draft.generation_metadata.get(
            "quality_advice",
            {},
        ).get(
            "decision",
            "",
        ),
        quality_data={
            "action": "teacher_reject",
            "quality": draft.generation_metadata.get(
                "quality",
                {},
            ),
            "advice": draft.generation_metadata.get(
                "quality_advice",
                {},
            ),
        },
    )

    return redirect(
        "intelligence:"
        "generated_draft_detail",
        draft_id=draft.pk,
    )