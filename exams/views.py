import csv
import secrets
import string

from datetime import (
    date,
    datetime,
    time,
)
from decimal import Decimal
from uuid import UUID

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import (
    Max,
    Q,
    Sum,
)
from django.http import HttpResponse

from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone
from django.views.decorators.http import (
    require_http_methods,
)

from accounts.decorators import (
    approved_teacher_required,
)

from assessment.models import Question

from .forms import (
    ExamForm,
    ExamQuestionFormSet,
)

from .models import (
    Exam,
    ExamAttempt,
    ExamEvent,
    ExamQuestion,
)


ACCESS_CODE_ALPHABET = (
    "ABCDEFGHJKLMNPQRSTUVWXYZ"
    "23456789"
)


def _get_teacher_exam(
    request,
    pk,
):
    return get_object_or_404(
        Exam.objects.select_related(
            "owner",
        ),
        pk=pk,
        owner=request.user,
    )


def _question_allowed_for_teacher(
    question,
    teacher,
):
    if question.owner_id == teacher.pk:
        return True

    if (
        getattr(
            question,
            "source_type",
            None,
        )
        == "SEED"
    ):
        return True

    return False


def _json_safe(value):

    if value is None:
        return None

    if isinstance(
        value,
        (
            str,
            int,
            float,
            bool,
        ),
    ):
        return value

    if isinstance(
        value,
        Decimal,
    ):
        return str(value)

    if isinstance(
        value,
        (
            datetime,
            date,
            time,
        ),
    ):
        return value.isoformat()

    if isinstance(
        value,
        UUID,
    ):
        return str(value)

    if isinstance(
        value,
        dict,
    ):
        return {
            str(key): _json_safe(item)
            for key, item
            in value.items()
        }

    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [
            _json_safe(item)
            for item in value
        ]

    return str(value)


def _build_question_snapshot(
    question,
):

    fields = {}

    for field in (
        question._meta.concrete_fields
    ):
        attribute_name = (
            field.attname
        )

        value = getattr(
            question,
            attribute_name,
        )

        fields[attribute_name] = (
            _json_safe(value)
        )

    return {
        "model": (
            question._meta.label
        ),
        "question_id": question.pk,
        "version": getattr(
            question,
            "version",
            1,
        ),
        "captured_at": (
            timezone.now().isoformat()
        ),
        "fields": fields,
    }


def _generate_access_code(
    length=8,
):

    for _ in range(100):

        code = "".join(
            secrets.choice(
                ACCESS_CODE_ALPHABET
            )
            for _ in range(length)
        )

        exists = (
            Exam.objects
            .filter(
                access_code=code,
            )
            .exists()
        )

        if not exists:
            return code

    raise RuntimeError(
        "Could not generate a unique "
        "exam access code."
    )


def _publish_exam(
    exam,
):
    """
    Publish an exam atomically.

    This function:
    - locks the Exam row,
    - validates ownership/schedule,
    - requires at least one question,
    - validates question access,
    - freezes question snapshots,
    - generates an access code,
    - records published_at,
    - changes status to PUBLISHED.
    """

    with transaction.atomic():

        locked_exam = (
            Exam.objects
            .select_for_update()
            .select_related(
                "owner",
            )
            .get(
                pk=exam.pk,
            )
        )

        if (
            locked_exam.status
            != Exam.Status.DRAFT
        ):
            raise ValidationError(
                {
                    "status": (
                        "Only draft exams "
                        "can be published."
                    )
                }
            )

        locked_exam.full_clean()

        exam_questions = list(
            locked_exam
            .exam_questions
            .select_related(
                "question",
            )
            .order_by(
                "order",
                "id",
            )
        )

        if not exam_questions:
            raise ValidationError(
                {
                    "questions": (
                        "An exam must contain "
                        "at least one question "
                        "before publication."
                    )
                }
            )

        for exam_question in (
            exam_questions
        ):

            question = (
                exam_question.question
            )

            if not (
                _question_allowed_for_teacher(
                    question,
                    locked_exam.owner,
                )
            ):
                raise ValidationError(
                    {
                        "questions": (
                            "The exam contains "
                            "a question that this "
                            "teacher is not allowed "
                            "to use."
                        )
                    }
                )

            question_version = (
                getattr(
                    question,
                    "version",
                    1,
                )
                or 1
            )

            exam_question.question_version = (
                question_version
            )

            exam_question.snapshot = (
                _build_question_snapshot(
                    question
                )
            )

            exam_question.full_clean()

            exam_question.save(
                update_fields=[
                    "question_version",
                    "snapshot",
                ]
            )

        if not locked_exam.access_code:
            locked_exam.access_code = (
                _generate_access_code()
            )

        locked_exam.status = (
            Exam.Status.PUBLISHED
        )

        locked_exam.published_at = (
            timezone.now()
        )

        locked_exam.full_clean()

        locked_exam.save(
            update_fields=[
                "access_code",
                "status",
                "published_at",
                "updated_at",
            ]
        )

        return locked_exam


@approved_teacher_required
def teacher_exam_list(
    request,
):

    exams = (
        Exam.objects
        .filter(
            owner=request.user,
        )
        .annotate(
            question_count=(
                models_count_questions()
            )
        )
        .order_by(
            "-created_at",
        )
    )

    return render(
        request,
        "exams/teacher/exam_list.html",
        {
            "exams": exams,
        },
    )


def models_count_questions():
    """
    Kept as a tiny helper so view declarations
    remain easy to read.
    """
    from django.db.models import Count

    return Count(
        "exam_questions",
        distinct=True,
    )


@approved_teacher_required
@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
def teacher_exam_create(
    request,
):

    exam = Exam(
        owner=request.user,
    )

    form = ExamForm(
        request.POST or None,
        instance=exam,
    )

    if (
        request.method == "POST"
        and form.is_valid()
    ):
        exam = form.save()

        messages.success(
            request,
            "Exam created successfully.",
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    return render(
        request,
        "exams/teacher/exam_form.html",
        {
            "form": form,
            "exam": exam,
            "page_title": "Create Exam",
        },
    )


@approved_teacher_required
@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
def teacher_exam_edit(
    request,
    pk,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    if (
        exam.status
        != Exam.Status.DRAFT
    ):
        messages.error(
            request,
            "Published or closed exams "
            "cannot be edited.",
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    form = ExamForm(
        request.POST or None,
        instance=exam,
    )

    if (
        request.method == "POST"
        and form.is_valid()
    ):
        form.save()

        messages.success(
            request,
            "Exam settings updated.",
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    return render(
        request,
        "exams/teacher/exam_form.html",
        {
            "form": form,
            "exam": exam,
            "page_title": "Edit Exam",
        },
    )


@approved_teacher_required
def teacher_exam_detail(
    request,
    pk,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    exam_questions = (
        exam.exam_questions
        .select_related(
            "question",
        )
        .order_by(
            "order",
            "id",
        )
    )

    total_points = (
        exam_questions
        .aggregate(
            total=Sum(
                "points"
            )
        )
        .get(
            "total"
        )
        or Decimal("0.00")
    )

    return render(
        request,
        "exams/teacher/exam_detail.html",
        {
            "exam": exam,
            "exam_questions": (
                exam_questions
            ),
            "question_count": (
                exam_questions.count()
            ),
            "total_points": (
                total_points
            ),
        },
    )


@approved_teacher_required
@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
def teacher_exam_question_bank(
    request,
    pk,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    if (
        exam.status
        != Exam.Status.DRAFT
    ):
        messages.error(
            request,
            "Questions can only be added "
            "to draft exams.",
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    allowed_questions = (
        Question.objects
        .filter(
            Q(
                owner=request.user
            )
            |
            Q(
                source_type="SEED"
            )
        )
        .distinct()
    )

    if request.method == "POST":

        selected_ids = (
            request.POST.getlist(
                "question_ids"
            )
        )

        if not selected_ids:
            messages.warning(
                request,
                "No questions were selected.",
            )

            return redirect(
                "exams:teacher_exam_question_bank",
                pk=exam.pk,
            )

        selected_questions = list(
            allowed_questions
            .filter(
                pk__in=selected_ids,
            )
            .order_by(
                "pk",
            )
        )

        already_linked = set(
            exam.exam_questions
            .values_list(
                "question_id",
                flat=True,
            )
        )

        next_order = (
            exam.exam_questions
            .aggregate(
                maximum=Max(
                    "order"
                )
            )
            .get(
                "maximum"
            )
            or 0
        )

        added_count = 0

        with transaction.atomic():

            for question in (
                selected_questions
            ):

                if (
                    question.pk
                    in already_linked
                ):
                    continue

                next_order += 1

                ExamQuestion.objects.create(
                    exam=exam,
                    question=question,
                    order=next_order,
                    points=Decimal(
                        "1.00"
                    ),
                    required=True,
                    question_version=(
                        getattr(
                            question,
                            "version",
                            1,
                        )
                        or 1
                    ),
                )

                added_count += 1

        messages.success(
            request,
            (
                f"{added_count} question(s) "
                "added to the exam."
            ),
        )

        return redirect(
            "exams:teacher_exam_structure",
            pk=exam.pk,
        )

    query = (
        request.GET
        .get(
            "q",
            "",
        )
        .strip()
    )

    visible_questions = (
        allowed_questions
    )

    if query:
        visible_questions = (
            visible_questions
            .filter(
                Q(
                    question_text__icontains=query
                )
                |
                Q(
                    explanation__icontains=query
                )
            )
        )

    visible_questions = (
        visible_questions
        .select_related(
            "domain_ref",
            "topic_ref",
            "owner",
        )
        .order_by(
            "domain_ref__name",
            "question_text",
        )
    )

    paginator = Paginator(
        visible_questions,
        25,
    )

    page_obj = paginator.get_page(
        request.GET.get(
            "page"
        )
    )

    already_linked_ids = set(
        exam.exam_questions
        .values_list(
            "question_id",
            flat=True,
        )
    )

    return render(
        request,
        "exams/teacher/question_bank.html",
        {
            "exam": exam,
            "page_obj": page_obj,
            "query": query,
            "already_linked_ids": (
                already_linked_ids
            ),
        },
    )


@approved_teacher_required
@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
def teacher_exam_structure(
    request,
    pk,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    if (
        exam.status
        != Exam.Status.DRAFT
    ):
        messages.error(
            request,
            "Published or closed exam "
            "structure cannot be changed.",
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    queryset = (
        exam.exam_questions
        .select_related(
            "question",
        )
        .order_by(
            "order",
            "id",
        )
    )

    formset = ExamQuestionFormSet(
        request.POST or None,
        instance=exam,
        queryset=queryset,
        prefix="questions",
    )

    if (
        request.method == "POST"
        and formset.is_valid()
    ):

        with transaction.atomic():
            formset.save()

        messages.success(
            request,
            "Exam question structure updated.",
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    return render(
        request,
        "exams/teacher/exam_structure.html",
        {
            "exam": exam,
            "formset": formset,
        },
    )


@approved_teacher_required
@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
def teacher_exam_publish(
    request,
    pk,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    if (
        exam.status
        != Exam.Status.DRAFT
    ):
        messages.info(
            request,
            "This exam is not in Draft status.",
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    if request.method == "POST":

        try:
            exam = _publish_exam(
                exam
            )

        except ValidationError as exc:

            messages.error(
                request,
                " ".join(
                    exc.messages
                ),
            )

            return redirect(
                "exams:teacher_exam_publish",
                pk=exam.pk,
            )

        except RuntimeError as exc:

            messages.error(
                request,
                str(exc),
            )

            return redirect(
                "exams:teacher_exam_publish",
                pk=exam.pk,
            )

        messages.success(
            request,
            (
                "Exam published successfully. "
                f"Access code: "
                f"{exam.access_code}"
            ),
        )

        return redirect(
            "exams:teacher_exam_detail",
            pk=exam.pk,
        )

    exam_questions = (
        exam.exam_questions
        .select_related(
            "question",
        )
        .order_by(
            "order",
        )
    )

    total_points = (
        exam_questions
        .aggregate(
            total=Sum(
                "points"
            )
        )
        .get(
            "total"
        )
        or Decimal("0.00")
    )

    return render(
        request,
        "exams/teacher/exam_publish.html",
        {
            "exam": exam,
            "exam_questions": (
                exam_questions
            ),
            "question_count": (
                exam_questions.count()
            ),
            "total_points": (
                total_points
            ),
        },
    )


# =========================================================
# UI-07 Exam Integrity Analytics
# =========================================================

INTEGRITY_EVENT_WEIGHTS = {
    "TAB_HIDDEN": 8,
    "WINDOW_BLUR": 4,
    "FULLSCREEN_EXIT": 10,
    "FULLSCREEN_REQUEST_FAILED": 0,
    "COPY_BLOCKED": 6,
    "CUT_BLOCKED": 6,
    "PASTE_BLOCKED": 8,
    "CONTEXT_MENU_BLOCKED": 2,
    "DRAG_BLOCKED": 2,
    "DROP_BLOCKED": 2,
    "SHORTCUT_BLOCKED": 5,
    "PRINT_ATTEMPT": 12,
    "SCREENSHOT_KEY": 12,
    "TRANSLATION_DETECTED": 18,
}


INTEGRITY_EVENT_LABELS = {
    "TAB_HIDDEN": "Tab switch / hidden tab",
    "WINDOW_BLUR": "Window focus lost",
    "FULLSCREEN_EXIT": "Fullscreen exit",
    "FULLSCREEN_REQUEST_FAILED": (
        "Fullscreen unavailable"
    ),
    "COPY_BLOCKED": "Copy attempt",
    "CUT_BLOCKED": "Cut attempt",
    "PASTE_BLOCKED": "Paste attempt",
    "CONTEXT_MENU_BLOCKED": (
        "Context menu attempt"
    ),
    "DRAG_BLOCKED": "Drag attempt",
    "DROP_BLOCKED": "Drop attempt",
    "SHORTCUT_BLOCKED": (
        "Restricted browser shortcut"
    ),
    "PRINT_ATTEMPT": "Print attempt",
    "SCREENSHOT_KEY": "Screenshot key",
    "TRANSLATION_DETECTED": (
        "Translation signal detected"
    ),
}


def _build_integrity_summary(
    attempt,
):
    """
    Build evidence-based browser integrity metrics.

    The score is a rule-based prioritization signal.
    It is not an automatic cheating verdict.
    """

    events = list(
        attempt.events
        .all()
        .order_by(
            "occurred_at",
            "id",
        )
    )

    security_events = []
    kind_counts = {}

    secure_mode_started = False

    for event in events:

        if (
            event.event_type
            == ExamEvent.EventType.SECURE_MODE_STARTED
        ):
            secure_mode_started = True
            continue

        if (
            event.event_type
            != ExamEvent.EventType.SECURITY_VIOLATION
        ):
            continue

        payload = (
            event.payload
            if isinstance(
                event.payload,
                dict,
            )
            else {}
        )

        kind = str(
            payload.get(
                "kind",
                "UNKNOWN",
            )
        ).strip().upper()

        kind_counts[kind] = (
            kind_counts.get(
                kind,
                0,
            )
            + 1
        )

        weight = (
            INTEGRITY_EVENT_WEIGHTS
            .get(
                kind,
                1,
            )
        )

        security_events.append(
            {
                "event": event,
                "kind": kind,
                "label": (
                    INTEGRITY_EVENT_LABELS
                    .get(
                        kind,
                        kind.replace(
                            "_",
                            " ",
                        ).title(),
                    )
                ),
                "weight": weight,
                "payload": payload,
            }
        )

    raw_score = 0

    contributions = []

    for kind, count in (
        kind_counts.items()
    ):

        weight = (
            INTEGRITY_EVENT_WEIGHTS
            .get(
                kind,
                1,
            )
        )

        contribution = (
            weight * count
        )

        raw_score += contribution

        if contribution > 0:

            contributions.append(
                {
                    "kind": kind,
                    "label": (
                        INTEGRITY_EVENT_LABELS
                        .get(
                            kind,
                            kind.replace(
                                "_",
                                " ",
                            ).title(),
                        )
                    ),
                    "count": count,
                    "weight": weight,
                    "contribution": (
                        contribution
                    ),
                }
            )

    score = min(
        int(raw_score),
        100,
    )

    if score >= 30:

        risk_level = "HIGH"

    elif score >= 10:

        risk_level = "MEDIUM"

    else:

        risk_level = "LOW"

    contributions.sort(
        key=lambda item: (
            item[
                "contribution"
            ],
            item["count"],
        ),
        reverse=True,
    )

    return {
        "score": score,
        "raw_score": raw_score,
        "risk_level": risk_level,
        "event_count": len(
            security_events
        ),
        "secure_mode_started": (
            secure_mode_started
        ),
        "kind_counts": kind_counts,
        "events": security_events,
        "reasons": contributions[:5],
    }


@approved_teacher_required
def teacher_integrity_dashboard(
    request,
):

    secure_exams = (
        Exam.objects
        .filter(
            owner=request.user,
            mode=Exam.Mode.SECURE,
        )
        .prefetch_related(
            "attempts",
            "attempts__student",
            "attempts__events",
        )
        .order_by(
            "-created_at",
        )
    )

    exam_rows = []

    total_attempts = 0
    high_risk_count = 0
    medium_risk_count = 0
    pending_review_count = 0

    recent_attempts = []

    for exam in secure_exams:

        attempt_rows = []

        for attempt in (
            exam.attempts
            .all()
            .order_by(
                "-started_at",
            )
        ):

            summary = (
                _build_integrity_summary(
                    attempt
                )
            )

            attempt_rows.append(
                {
                    "attempt": attempt,
                    "summary": summary,
                }
            )

            recent_attempts.append(
                {
                    "exam": exam,
                    "attempt": attempt,
                    "summary": summary,
                }
            )

            total_attempts += 1

            if (
                summary[
                    "risk_level"
                ]
                == "HIGH"
            ):
                high_risk_count += 1

            elif (
                summary[
                    "risk_level"
                ]
                == "MEDIUM"
            ):
                medium_risk_count += 1

            if (
                attempt.integrity_decision
                == ExamAttempt
                .IntegrityDecision
                .PENDING
            ):
                pending_review_count += 1

        exam_rows.append(
            {
                "exam": exam,
                "attempt_count": len(
                    attempt_rows
                ),
                "high_count": sum(
                    1
                    for row
                    in attempt_rows
                    if (
                        row[
                            "summary"
                        ][
                            "risk_level"
                        ]
                        == "HIGH"
                    )
                ),
                "medium_count": sum(
                    1
                    for row
                    in attempt_rows
                    if (
                        row[
                            "summary"
                        ][
                            "risk_level"
                        ]
                        == "MEDIUM"
                    )
                ),
            }
        )

    recent_attempts.sort(
        key=lambda row: (
            row[
                "attempt"
            ].started_at
        ),
        reverse=True,
    )

    return render(
        request,
        "exams/teacher/integrity_dashboard.html",
        {
            "exam_rows": exam_rows,
            "secure_exam_count": (
                len(
                    exam_rows
                )
            ),
            "total_attempts": (
                total_attempts
            ),
            "high_risk_count": (
                high_risk_count
            ),
            "medium_risk_count": (
                medium_risk_count
            ),
            "pending_review_count": (
                pending_review_count
            ),
            "recent_attempts": (
                recent_attempts[:20]
            ),
        },
    )


@approved_teacher_required
def teacher_exam_integrity(
    request,
    pk,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    attempts = (
        exam.attempts
        .select_related(
            "student",
            "integrity_reviewed_by",
        )
        .prefetch_related(
            "events",
        )
        .order_by(
            "-started_at",
        )
    )

    rows = []

    for attempt in attempts:

        rows.append(
            {
                "attempt": attempt,
                "summary": (
                    _build_integrity_summary(
                        attempt
                    )
                ),
            }
        )

    return render(
        request,
        "exams/teacher/exam_integrity.html",
        {
            "exam": exam,
            "rows": rows,
            "attempt_count": len(
                rows
            ),
            "high_count": sum(
                1
                for row in rows
                if (
                    row["summary"]
                    ["risk_level"]
                    == "HIGH"
                )
            ),
            "medium_count": sum(
                1
                for row in rows
                if (
                    row["summary"]
                    ["risk_level"]
                    == "MEDIUM"
                )
            ),
            "low_count": sum(
                1
                for row in rows
                if (
                    row["summary"]
                    ["risk_level"]
                    == "LOW"
                )
            ),
        },
    )


@approved_teacher_required
@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
def teacher_attempt_integrity(
    request,
    pk,
    attempt_id,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    attempt = get_object_or_404(
        ExamAttempt.objects
        .select_related(
            "student",
            "integrity_reviewed_by",
        )
        .prefetch_related(
            "events",
        ),
        pk=attempt_id,
        exam=exam,
    )

    if request.method == "POST":

        decision = (
            request.POST
            .get(
                "integrity_decision",
                "",
            )
            .strip()
        )

        valid_decisions = {
            value
            for value, _
            in (
                ExamAttempt
                .IntegrityDecision
                .choices
            )
        }

        if decision not in (
            valid_decisions
        ):

            messages.error(
                request,
                "Invalid integrity decision.",
            )

            return redirect(
                "exams:teacher_attempt_integrity",
                pk=exam.pk,
                attempt_id=attempt.pk,
            )

        note = (
            request.POST
            .get(
                "integrity_review_note",
                "",
            )
            .strip()
        )[:3000]

        attempt.integrity_decision = (
            decision
        )

        attempt.integrity_review_note = (
            note
        )

        attempt.integrity_reviewed_by = (
            request.user
        )

        attempt.integrity_reviewed_at = (
            timezone.now()
        )

        attempt.save(
            update_fields=[
                "integrity_decision",
                "integrity_review_note",
                "integrity_reviewed_by",
                "integrity_reviewed_at",
                "last_activity_at",
            ]
        )

        messages.success(
            request,
            "Integrity review saved.",
        )

        return redirect(
            "exams:teacher_attempt_integrity",
            pk=exam.pk,
            attempt_id=attempt.pk,
        )

    summary = (
        _build_integrity_summary(
            attempt
        )
    )

    return render(
        request,
        "exams/teacher/attempt_integrity.html",
        {
            "exam": exam,
            "attempt": attempt,
            "summary": summary,
            "decision_choices": (
                ExamAttempt
                .IntegrityDecision
                .choices
            ),
        },
    )


@approved_teacher_required
def teacher_exam_integrity_export(
    request,
    pk,
):

    exam = _get_teacher_exam(
        request,
        pk,
    )

    attempts = (
        exam.attempts
        .select_related(
            "student",
            "integrity_reviewed_by",
        )
        .prefetch_related(
            "events",
        )
        .order_by(
            "started_at",
        )
    )

    response = HttpResponse(
        content_type=(
            "text/csv; charset=utf-8"
        )
    )

    response[
        "Content-Disposition"
    ] = (
        'attachment; filename="'
        f'exam_{exam.pk}_integrity.csv"'
    )

    response.write(
        "\ufeff"
    )

    writer = csv.writer(
        response
    )

    writer.writerow(
        [
            "exam_id",
            "exam_title",
            "attempt_id",
            "student",
            "attempt_number",
            "attempt_status",
            "percentage",
            "risk_score",
            "risk_level",
            "security_event_count",
            "secure_mode_started",
            "integrity_decision",
            "reviewed_by",
            "reviewed_at",
            "review_note",
            "event_counts",
        ]
    )

    for attempt in attempts:

        summary = (
            _build_integrity_summary(
                attempt
            )
        )

        counts_text = "; ".join(
            (
                f"{kind}={count}"
            )
            for kind, count
            in sorted(
                summary[
                    "kind_counts"
                ].items()
            )
        )

        writer.writerow(
            [
                exam.pk,
                exam.title,
                attempt.pk,
                attempt.student.username,
                attempt.attempt_number,
                attempt.status,
                (
                    attempt.percentage
                    if (
                        attempt.percentage
                        is not None
                    )
                    else ""
                ),
                summary["score"],
                summary[
                    "risk_level"
                ],
                summary[
                    "event_count"
                ],
                summary[
                    "secure_mode_started"
                ],
                attempt.integrity_decision,
                (
                    attempt
                    .integrity_reviewed_by
                    .username
                    if (
                        attempt
                        .integrity_reviewed_by
                    )
                    else ""
                ),
                (
                    attempt
                    .integrity_reviewed_at
                    .isoformat()
                    if (
                        attempt
                        .integrity_reviewed_at
                    )
                    else ""
                ),
                attempt.integrity_review_note,
                counts_text,
            ]
        )

    return response


