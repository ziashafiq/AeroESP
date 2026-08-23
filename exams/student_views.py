import secrets

from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import (
    require_GET,
    require_http_methods,
    require_POST,
)

from accounts.decorators import student_required

from .models import (
    Exam,
    ExamAttempt,
    ExamEvent,
    ExamQuestion,
    StudentAnswer,
)

from .student_forms import ExamAccessCodeForm


# =========================================================
# Access
# =========================================================


def _access_session_key(exam_id):
    return f"aeroesp_exam_access_{exam_id}"


def _grant_exam_access(
    request,
    exam,
):
    request.session[
        _access_session_key(exam.pk)
    ] = exam.access_code


def _has_exam_access(
    request,
    exam,
):

    # A student who already owns an Attempt
    # retains access to that Exam.
    has_attempt = (
        ExamAttempt.objects
        .filter(
            exam=exam,
            student=request.user,
        )
        .exists()
    )

    if has_attempt:
        return True

    session_code = (
        request.session.get(
            _access_session_key(
                exam.pk
            )
        )
    )

    return (
        session_code
        and exam.access_code
        and session_code
        == exam.access_code
    )


# =========================================================
# Snapshot helpers
# =========================================================


def _snapshot_fields(
    exam_question,
):
    return (
        exam_question.snapshot
        .get(
            "fields",
            {},
        )
    )


def _first_value(
    fields,
    names,
    default=None,
):

    for name in names:

        if name in fields:
            value = fields[name]

            if value not in (
                None,
                "",
            ):
                return value

    return default


def _snapshot_question_text(
    exam_question,
):

    fields = _snapshot_fields(
        exam_question
    )

    return _first_value(
        fields,
        (
            "question_text",
            "text",
            "prompt",
        ),
        default=(
            "Question text unavailable"
        ),
    )


def _snapshot_correct_choice(
    exam_question,
):

    fields = _snapshot_fields(
        exam_question
    )

    value = _first_value(
        fields,
        (
            "correct_answer",
            "correct_option",
            "correct_choice",
            "answer",
        ),
    )

    if value is None:
        return None

    value = str(value).strip().upper()

    if value in {
        "A",
        "B",
        "C",
        "D",
    }:
        return value

    return None


def _snapshot_options(
    exam_question,
    option_order,
):

    fields = _snapshot_fields(
        exam_question
    )

    candidate_names = {
        "A": (
            "option_a",
            "choice_a",
            "answer_a",
        ),
        "B": (
            "option_b",
            "choice_b",
            "answer_b",
        ),
        "C": (
            "option_c",
            "choice_c",
            "answer_c",
        ),
        "D": (
            "option_d",
            "choice_d",
            "answer_d",
        ),
    }

    option_map = {}

    # Standard A-D fields.
    for key in (
        "A",
        "B",
        "C",
        "D",
    ):
        option_map[key] = _first_value(
            fields,
            candidate_names[key],
            default="",
        )

    # Fallback for a possible JSON/list
    # "options" field.
    raw_options = fields.get(
        "options"
    )

    if isinstance(
        raw_options,
        dict,
    ):
        for key in (
            "A",
            "B",
            "C",
            "D",
        ):
            if not option_map[key]:
                option_map[key] = (
                    raw_options.get(key)
                    or raw_options.get(
                        key.lower()
                    )
                    or ""
                )

    elif isinstance(
        raw_options,
        list,
    ):
        for index, key in enumerate(
            (
                "A",
                "B",
                "C",
                "D",
            )
        ):
            if (
                index
                < len(raw_options)
                and not option_map[key]
            ):
                option_map[key] = (
                    raw_options[index]
                )

    return [
        {
            "key": key,
            "text": option_map.get(
                key,
                "",
            ),
        }
        for key in option_order
    ]


# =========================================================
# Presentation plan
# =========================================================


def _build_presentation_plan(
    exam,
    exam_questions,
):

    question_order = [
        item.pk
        for item in exam_questions
    ]

    randomizer = (
        secrets.SystemRandom()
    )

    if exam.shuffle_questions:
        randomizer.shuffle(
            question_order
        )

    option_orders = {}

    for item in exam_questions:

        choices = [
            "A",
            "B",
            "C",
            "D",
        ]

        if exam.shuffle_options:
            randomizer.shuffle(
                choices
            )

        option_orders[
            str(item.pk)
        ] = choices

    return {
        "question_order": (
            question_order
        ),
        "option_orders": (
            option_orders
        ),
        "shuffle_questions": (
            exam.shuffle_questions
        ),
        "shuffle_options": (
            exam.shuffle_options
        ),
    }


def _get_presentation_plan(
    attempt,
):

    event = (
        attempt.events
        .filter(
            event_type=(
                ExamEvent.EventType
                .ATTEMPT_STARTED
            )
        )
        .order_by(
            "occurred_at",
            "id",
        )
        .first()
    )

    if event:
        plan = event.payload.get(
            "presentation"
        )

        if plan:
            return plan

    # Defensive fallback.
    exam_questions = list(
        attempt.exam
        .exam_questions
        .order_by(
            "order",
            "id",
        )
    )

    return _build_presentation_plan(
        attempt.exam,
        exam_questions,
    )


# =========================================================
# Attempt lifecycle
# =========================================================


def _start_attempt(
    exam,
    student,
):

    User = get_user_model()

    with transaction.atomic():

        # Serialize concurrent starts
        # for the same student.
        User.objects.select_for_update().get(
            pk=student.pk
        )

        exam = (
            Exam.objects
            .select_for_update()
            .get(
                pk=exam.pk
            )
        )

        now = timezone.now()

        if not exam.is_available_at(
            now
        ):
            raise ValidationError(
                "This exam is not currently "
                "available."
            )

        active_attempt = (
            ExamAttempt.objects
            .filter(
                exam=exam,
                student=student,
                status=(
                    ExamAttempt.Status
                    .IN_PROGRESS
                ),
            )
            .first()
        )

        if active_attempt:
            return (
                active_attempt,
                False,
            )

        last_attempt_number = (
            ExamAttempt.objects
            .filter(
                exam=exam,
                student=student,
            )
            .aggregate(
                maximum=Max(
                    "attempt_number"
                )
            )[
                "maximum"
            ]
            or 0
        )

        next_attempt_number = (
            last_attempt_number + 1
        )

        if (
            next_attempt_number
            > exam.max_attempts
        ):
            raise ValidationError(
                "Maximum number of attempts "
                "has already been reached."
            )

        exam_questions = list(
            exam.exam_questions
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
                "This exam contains no "
                "questions."
            )

        for item in exam_questions:
            if not item.snapshot:
                raise ValidationError(
                    "This published exam has "
                    "an unfrozen question."
                )

        started_at = now

        deadline_at = (
            started_at
            + timedelta(
                minutes=(
                    exam.duration_minutes
                )
            )
        )

        if (
            exam.ends_at
            and exam.ends_at
            < deadline_at
        ):
            deadline_at = (
                exam.ends_at
            )

        if deadline_at <= started_at:
            raise ValidationError(
                "The exam time window "
                "has already ended."
            )

        attempt = ExamAttempt(
            exam=exam,
            student=student,
            attempt_number=(
                next_attempt_number
            ),
            status=(
                ExamAttempt.Status
                .IN_PROGRESS
            ),
            started_at=started_at,
            deadline_at=deadline_at,
        )

        attempt.full_clean()
        attempt.save()

        StudentAnswer.objects.bulk_create(
            [
                StudentAnswer(
                    attempt=attempt,
                    exam_question=item,
                )
                for item
                in exam_questions
            ]
        )

        presentation = (
            _build_presentation_plan(
                exam,
                exam_questions,
            )
        )

        ExamEvent.objects.create(
            attempt=attempt,
            event_type=(
                ExamEvent.EventType
                .ATTEMPT_STARTED
            ),
            payload={
                "presentation": (
                    presentation
                ),
                "deadline_at": (
                    deadline_at.isoformat()
                ),
            },
        )

        return (
            attempt,
            True,
        )


def _deadline_passed(
    attempt,
):

    return bool(
        attempt.deadline_at
        and timezone.now()
        >= attempt.deadline_at
    )


def _save_answer(
    attempt,
    exam_question,
    selected_answer,
    client_elapsed_ms=0,
):

    selected_answer = (
        str(selected_answer)
        .strip()
        .upper()
    )

    if selected_answer not in {
        "A",
        "B",
        "C",
        "D",
    }:
        raise ValidationError(
            "Invalid answer choice."
        )

    if (
        exam_question.exam_id
        != attempt.exam_id
    ):
        raise ValidationError(
            "Question does not belong "
            "to this attempt."
        )

    try:
        client_elapsed_ms = int(
            client_elapsed_ms or 0
        )
    except (
        TypeError,
        ValueError,
    ):
        client_elapsed_ms = 0

    # This is supplemental client
    # telemetry, not the authoritative
    # server timer.
    client_elapsed_ms = max(
        0,
        min(
            client_elapsed_ms,
            600000,
        ),
    )

    with transaction.atomic():

        answer = (
            StudentAnswer.objects
            .select_for_update()
            .get(
                attempt=attempt,
                exam_question=(
                    exam_question
                ),
            )
        )

        previous = (
            answer.selected_answer
        )

        changed = bool(
            previous
            and previous
            != selected_answer
        )

        now = timezone.now()

        if not answer.first_answered_at:
            answer.first_answered_at = (
                now
            )

        if changed:
            answer.answer_change_count += 1

        answer.selected_answer = (
            selected_answer
        )

        answer.last_answered_at = (
            now
        )

        answer.time_spent_ms += (
            client_elapsed_ms
        )

        correct_choice = (
            _snapshot_correct_choice(
                exam_question
            )
        )

        if correct_choice:
            answer.is_correct = (
                selected_answer
                == correct_choice
            )
        else:
            answer.is_correct = None

        answer.awarded_points = (
            exam_question.points
            if answer.is_correct
            else Decimal("0.00")
        )

        answer.full_clean()

        answer.save(
            update_fields=[
                "selected_answer",
                "is_correct",
                "awarded_points",
                "first_answered_at",
                "last_answered_at",
                "answer_change_count",
                "time_spent_ms",
                "updated_at",
            ]
        )

        ExamAttempt.objects.filter(
            pk=attempt.pk,
        ).update(
            last_activity_at=now,
        )
        ExamEvent.objects.create(
            attempt=attempt,
            exam_question=(
                exam_question
            ),
            event_type=(
                ExamEvent.EventType
                .ANSWER_CHANGED
                if changed
                else
                ExamEvent.EventType
                .ANSWER_SAVED
            ),
            payload={
                "selected_answer": (
                    selected_answer
                ),
                "client_elapsed_ms": (
                    client_elapsed_ms
                ),
            },
        )

        return answer


def _finalize_attempt(
    attempt,
    *,
    auto_submit=False,
):

    with transaction.atomic():

        attempt = (
            ExamAttempt.objects
            .select_for_update()
            .select_related(
                "exam",
            )
            .get(
                pk=attempt.pk
            )
        )

        if (
            attempt.status
            != ExamAttempt.Status
            .IN_PROGRESS
        ):
            return attempt

        answers = list(
            attempt.answers
            .select_related(
                "exam_question",
            )
        )

        max_score = Decimal(
            "0.00"
        )

        score = Decimal(
            "0.00"
        )

        for answer in answers:

            exam_question = (
                answer.exam_question
            )

            max_score += (
                exam_question.points
            )

            correct_choice = (
                _snapshot_correct_choice(
                    exam_question
                )
            )

            selected = (
                answer.selected_answer
                or ""
            )

            if correct_choice:
                is_correct = (
                    selected
                    == correct_choice
                )
            else:
                is_correct = None

            awarded = (
                exam_question.points
                if is_correct
                else Decimal(
                    "0.00"
                )
            )

            answer.is_correct = (
                is_correct
            )

            answer.awarded_points = (
                awarded
            )

            answer.save(
                update_fields=[
                    "is_correct",
                    "awarded_points",
                    "updated_at",
                ]
            )

            score += awarded

        if max_score > 0:
            percentage = (
                score
                / max_score
                * Decimal("100")
            ).quantize(
                Decimal("0.01")
            )
        else:
            percentage = Decimal(
                "0.00"
            )

        attempt.score = score
        attempt.max_score = (
            max_score
        )
        attempt.percentage = (
            percentage
        )
        attempt.submitted_at = (
            timezone.now()
        )

        if auto_submit:
            attempt.status = (
                ExamAttempt.Status
                .AUTO_SUBMITTED
            )
            event_type = (
                ExamEvent.EventType
                .AUTO_SUBMITTED
            )
        else:
            attempt.status = (
                ExamAttempt.Status
                .SUBMITTED
            )
            event_type = (
                ExamEvent.EventType
                .SUBMITTED
            )

        attempt.full_clean()

        attempt.save(
            update_fields=[
                "score",
                "max_score",
                "percentage",
                "submitted_at",
                "status",
                "last_activity_at",
            ]
        )

        ExamEvent.objects.create(
            attempt=attempt,
            event_type=event_type,
            payload={
                "score": str(
                    score
                ),
                "max_score": str(
                    max_score
                ),
                "percentage": str(
                    percentage
                ),
            },
        )

        return attempt


def _result_is_visible(
    exam,
):

    if (
        exam.result_policy
        == Exam.ResultPolicy.IMMEDIATE
    ):
        return True

    if (
        exam.result_policy
        == Exam.ResultPolicy.AFTER_CLOSE
    ):

        if exam.status in {
            Exam.Status.CLOSED,
            Exam.Status.ARCHIVED,
        }:
            return True

        if (
            exam.ends_at
            and timezone.now()
            >= exam.ends_at
        ):
            return True

    # MANUAL requires a later
    # release workflow.
    return False


# =========================================================
# Student views
# =========================================================


@student_required
@require_http_methods(
    [
        "GET",
        "POST",
    ]
)
def student_exam_home(
    request,
):

    form = ExamAccessCodeForm(
        request.POST or None
    )

    if (
        request.method == "POST"
        and form.is_valid()
    ):
        exam = form.exam

        _grant_exam_access(
            request,
            exam,
        )

        return redirect(
            "exams_student:preview",
            pk=exam.pk,
        )

    attempts = (
        ExamAttempt.objects
        .filter(
            student=request.user,
        )
        .select_related(
            "exam",
        )
        .order_by(
            "-started_at",
        )
    )

    return render(
        request,
        "exams/student/home.html",
        {
            "form": form,
            "attempts": attempts,
        },
    )


@student_required
@require_GET
def student_exam_preview(
    request,
    pk,
):

    exam = get_object_or_404(
        Exam,
        pk=pk,
        status=Exam.Status.PUBLISHED,
    )

    if not _has_exam_access(
        request,
        exam,
    ):
        messages.error(
            request,
            "Enter the exam access code first.",
        )

        return redirect(
            "exams_student:home"
        )

    attempts = (
        ExamAttempt.objects
        .filter(
            exam=exam,
            student=request.user,
        )
        .order_by(
            "-attempt_number",
        )
    )

    active_attempt = (
        attempts
        .filter(
            status=(
                ExamAttempt.Status
                .IN_PROGRESS
            )
        )
        .first()
    )

    attempt_count = (
        attempts.count()
    )

    can_start = bool(
        active_attempt
        or (
            exam.is_available_at()
            and attempt_count
            < exam.max_attempts
        )
    )

    return render(
        request,
        "exams/student/preview.html",
        {
            "exam": exam,
            "active_attempt": (
                active_attempt
            ),
            "attempt_count": (
                attempt_count
            ),
            "can_start": can_start,
        },
    )


@student_required
@require_POST
def student_exam_start(
    request,
    pk,
):

    exam = get_object_or_404(
        Exam,
        pk=pk,
        status=Exam.Status.PUBLISHED,
    )

    if not _has_exam_access(
        request,
        exam,
    ):
        messages.error(
            request,
            "Exam access is not authorized.",
        )

        return redirect(
            "exams_student:home"
        )

    try:
        attempt, created = (
            _start_attempt(
                exam,
                request.user,
            )
        )

    except ValidationError as exc:

        messages.error(
            request,
            " ".join(
                exc.messages
            ),
        )

        return redirect(
            "exams_student:preview",
            pk=exam.pk,
        )

    if created:
        messages.success(
            request,
            "Exam attempt started.",
        )

    return redirect(
        "exams_student:take",
        attempt_id=attempt.pk,
    )


@student_required
@require_GET
def student_exam_take(
    request,
    attempt_id,
):

    attempt = get_object_or_404(
        ExamAttempt.objects
        .select_related(
            "exam",
        ),
        pk=attempt_id,
        student=request.user,
    )

    if (
        attempt.status
        == ExamAttempt.Status
        .IN_PROGRESS
        and _deadline_passed(
            attempt
        )
    ):
        attempt = _finalize_attempt(
            attempt,
            auto_submit=True,
        )

    if (
        attempt.status
        != ExamAttempt.Status
        .IN_PROGRESS
    ):
        return redirect(
            "exams_student:result",
            attempt_id=attempt.pk,
        )

    presentation = (
        _get_presentation_plan(
            attempt
        )
    )

    exam_questions = {
        item.pk: item
        for item
        in attempt.exam
        .exam_questions
        .all()
    }

    answers = {
        item.exam_question_id: (
            item
        )
        for item
        in attempt.answers.all()
    }

    items = []

    for question_id in (
        presentation.get(
            "question_order",
            [],
        )
    ):

        exam_question = (
            exam_questions.get(
                int(question_id)
            )
        )

        if not exam_question:
            continue

        option_order = (
            presentation
            .get(
                "option_orders",
                {},
            )
            .get(
                str(
                    exam_question.pk
                ),
                [
                    "A",
                    "B",
                    "C",
                    "D",
                ],
            )
        )

        answer = answers.get(
            exam_question.pk
        )

        items.append(
            {
                "exam_question": (
                    exam_question
                ),
                "text": (
                    _snapshot_question_text(
                        exam_question
                    )
                ),
                "options": (
                    _snapshot_options(
                        exam_question,
                        option_order,
                    )
                ),
                "selected": (
                    answer.selected_answer
                    if answer
                    else ""
                ),
                "flagged": (
                    answer.flagged_for_review
                    if answer
                    else False
                ),
                "flag_note": (
                    answer.flag_note
                    if answer
                    else ""
                ),
                "flag_url": reverse(
                    (
                        "exams_student:"
                        "save_flag"
                    ),
                    kwargs={
                        "attempt_id": (
                            attempt.pk
                        ),
                        "exam_question_id": (
                            exam_question.pk
                        ),
                    },
                ),
                "save_url": reverse(
                    (
                        "exams_student:"
                        "save_answer"
                    ),
                    kwargs={
                        "attempt_id": (
                            attempt.pk
                        ),
                        "exam_question_id": (
                            exam_question.pk
                        ),
                    },
                ),
            }
        )

    return render(
        request,
        "exams/student/take.html",
        {
            "attempt": attempt,
            "exam": attempt.exam,
            "items": items,
            "deadline_iso": (
                attempt.deadline_at
                .isoformat()
                if attempt.deadline_at
                else ""
            ),
        },
    )


@student_required
@require_POST
def student_save_answer(
    request,
    attempt_id,
    exam_question_id,
):

    attempt = get_object_or_404(
        ExamAttempt,
        pk=attempt_id,
        student=request.user,
    )

    if (
        attempt.status
        != ExamAttempt.Status
        .IN_PROGRESS
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Attempt is no longer active."
                ),
            },
            status=409,
        )

    if _deadline_passed(
        attempt
    ):
        _finalize_attempt(
            attempt,
            auto_submit=True,
        )

        return JsonResponse(
            {
                "ok": False,
                "expired": True,
            },
            status=409,
        )

    exam_question = (
        get_object_or_404(
            ExamQuestion,
            pk=exam_question_id,
            exam=attempt.exam,
        )
    )

    selected = (
        request.POST.get(
            "selected_answer",
            "",
        )
    )

    elapsed = (
        request.POST.get(
            "client_elapsed_ms",
            "0",
        )
    )

    try:
        answer = _save_answer(
            attempt,
            exam_question,
            selected,
            elapsed,
        )

    except ValidationError as exc:

        return JsonResponse(
            {
                "ok": False,
                "error": " ".join(
                    exc.messages
                ),
            },
            status=400,
        )

    return JsonResponse(
        {
            "ok": True,
            "selected_answer": (
                answer.selected_answer
            ),
            "answer_change_count": (
                answer.answer_change_count
            ),
        }
    )


@student_required
@require_POST
def student_event_log(
    request,
    attempt_id,
):

    attempt = get_object_or_404(
        ExamAttempt,
        pk=attempt_id,
        student=request.user,
        status=(
            ExamAttempt.Status
            .IN_PROGRESS
        ),
    )

    if _deadline_passed(
        attempt
    ):
        _finalize_attempt(
            attempt,
            auto_submit=True,
        )

        return JsonResponse(
            {
                "ok": False,
                "expired": True,
            },
            status=409,
        )

    event_type = (
        request.POST.get(
            "event_type",
            "",
        )
    )

    allowed = {
        ExamEvent.EventType.PAGE_FOCUS,
        ExamEvent.EventType.PAGE_BLUR,
        ExamEvent.EventType.RECONNECTED,
        ExamEvent.EventType.QUESTION_VIEWED,
    }

    if event_type not in allowed:
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Unsupported event type."
                ),
            },
            status=400,
        )

    exam_question = None

    if (
        event_type
        == ExamEvent.EventType
        .QUESTION_VIEWED
    ):
        exam_question_id = (
            request.POST.get(
                "exam_question_id"
            )
        )

        if not exam_question_id:
            return JsonResponse(
                {
                    "ok": False,
                    "error": (
                        "exam_question_id "
                        "is required."
                    ),
                },
                status=400,
            )

        exam_question = (
            get_object_or_404(
                ExamQuestion,
                pk=exam_question_id,
                exam=attempt.exam,
            )
        )

    event = ExamEvent(
        attempt=attempt,
        exam_question=exam_question,
        event_type=event_type,
        payload={
            "source": (
                "student_exam_ui"
            ),
        },
    )

    event.full_clean()
    event.save()

    ExamAttempt.objects.filter(
        pk=attempt.pk,
    ).update(
        last_activity_at=(
            timezone.now()
        ),
    )

    return JsonResponse(
        {
            "ok": True,
        }
    )


@student_required
@require_POST
def student_exam_submit(
    request,
    attempt_id,
):

    attempt = get_object_or_404(
        ExamAttempt,
        pk=attempt_id,
        student=request.user,
    )

    if (
        attempt.status
        == ExamAttempt.Status
        .IN_PROGRESS
    ):

        auto_submit = (
            _deadline_passed(
                attempt
            )
        )

        attempt = _finalize_attempt(
            attempt,
            auto_submit=auto_submit,
        )

    return redirect(
        "exams_student:result",
        attempt_id=attempt.pk,
    )


@student_required
@require_GET
def student_exam_result(
    request,
    attempt_id,
):

    attempt = get_object_or_404(
        ExamAttempt.objects
        .select_related(
            "exam",
        ),
        pk=attempt_id,
        student=request.user,
    )

    if (
        attempt.status
        == ExamAttempt.Status
        .IN_PROGRESS
        and _deadline_passed(
            attempt
        )
    ):
        attempt = _finalize_attempt(
            attempt,
            auto_submit=True,
        )

    if (
        attempt.status
        == ExamAttempt.Status
        .IN_PROGRESS
    ):
        return redirect(
            "exams_student:take",
            attempt_id=attempt.pk,
        )

    show_result = (
        _result_is_visible(
            attempt.exam
        )
    )

    flagged_answers = list(
        attempt.answers
        .filter(
            flagged_for_review=True,
        )
        .select_related(
            "exam_question",
            "exam_question__question",
        )
        .order_by(
            "exam_question__order",
        )
    )

    return render(
        request,
        "exams/student/result.html",
        {
            "attempt": attempt,
            "exam": attempt.exam,
            "show_result": (
                show_result
            ),
            "flagged_answers": (
                flagged_answers
            ),
        },
    )

@student_required
@require_POST
def student_save_flag(
    request,
    attempt_id,
    exam_question_id,
):

    attempt = get_object_or_404(
        ExamAttempt,
        pk=attempt_id,
        student=request.user,
    )

    if (
        attempt.status
        != ExamAttempt.Status.IN_PROGRESS
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": "Attempt is no longer active.",
            },
            status=409,
        )

    if _deadline_passed(attempt):

        _finalize_attempt(
            attempt,
            auto_submit=True,
        )

        return JsonResponse(
            {
                "ok": False,
                "expired": True,
            },
            status=409,
        )

    exam_question = get_object_or_404(
        ExamQuestion,
        pk=exam_question_id,
        exam=attempt.exam,
    )

    flagged_value = (
        request.POST
        .get(
            "flagged",
            "false",
        )
        .strip()
        .lower()
    )

    flagged = flagged_value in {
        "1",
        "true",
        "yes",
        "on",
    }

    note = (
        request.POST
        .get(
            "flag_note",
            "",
        )
        .strip()
    )

    if len(note) > 1000:
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Review note must be "
                    "1000 characters or fewer."
                ),
            },
            status=400,
        )

    answer, _ = (
        StudentAnswer.objects
        .get_or_create(
            attempt=attempt,
            exam_question=exam_question,
            defaults={
                "selected_answer": "",
            },
        )
    )

    answer.flagged_for_review = flagged
    answer.flag_note = (
        note
        if flagged
        else ""
    )

    answer.save(
        update_fields=[
            "flagged_for_review",
            "flag_note",
            "updated_at",
        ]
    )

    return JsonResponse(
        {
            "ok": True,
            "flagged": answer.flagged_for_review,
            "flag_note": answer.flag_note,
        }
    )


@student_required
@require_POST
def student_security_event(
    request,
    attempt_id,
):
    """
    Record browser-side integrity signals for SECURE exams.

    These events are evidence only.
    They do not automatically invalidate an attempt.
    """

    from .models import ExamEvent

    attempt = get_object_or_404(
        ExamAttempt.objects
        .select_related(
            "exam",
        ),
        pk=attempt_id,
        student=request.user,
    )

    if (
        attempt.status
        != ExamAttempt.Status.IN_PROGRESS
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Attempt is no longer active."
                ),
            },
            status=409,
        )

    if (
        attempt.exam.mode
        != Exam.Mode.SECURE
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Security telemetry is only "
                    "enabled for secure exams."
                ),
            },
            status=400,
        )

    if _deadline_passed(
        attempt
    ):
        _finalize_attempt(
            attempt,
            auto_submit=True,
        )

        return JsonResponse(
            {
                "ok": False,
                "expired": True,
            },
            status=409,
        )

    kind = (
        request.POST
        .get(
            "kind",
            "",
        )
        .strip()
        .upper()
    )

    allowed_kinds = {
        "SECURE_MODE_STARTED",
        "TAB_HIDDEN",
        "WINDOW_BLUR",
        "FULLSCREEN_EXIT",
        "FULLSCREEN_REQUEST_FAILED",
        "COPY_BLOCKED",
        "CUT_BLOCKED",
        "PASTE_BLOCKED",
        "CONTEXT_MENU_BLOCKED",
        "DRAG_BLOCKED",
        "DROP_BLOCKED",
        "SHORTCUT_BLOCKED",
        "PRINT_ATTEMPT",
        "SCREENSHOT_KEY",
        "TRANSLATION_DETECTED",
    }

    if kind not in allowed_kinds:

        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Unsupported security event."
                ),
            },
            status=400,
        )

    detail = (
        request.POST
        .get(
            "detail",
            "",
        )
        .strip()
    )[:250]

    client_time = (
        request.POST
        .get(
            "client_time",
            "",
        )
        .strip()
    )[:100]

    visibility = (
        request.POST
        .get(
            "visibility",
            "",
        )
        .strip()
    )[:30]

    fullscreen = (
        request.POST
        .get(
            "fullscreen",
            "",
        )
        .strip()
    )[:20]

    if kind == "SECURE_MODE_STARTED":

        event_type = (
            ExamEvent
            .EventType
            .SECURE_MODE_STARTED
        )

    else:

        event_type = (
            ExamEvent
            .EventType
            .SECURITY_VIOLATION
        )

    ExamEvent.objects.create(
        attempt=attempt,
        event_type=event_type,
        payload={
            "kind": kind,
            "detail": detail,
            "client_time": client_time,
            "visibility": visibility,
            "fullscreen": fullscreen,
        },
    )

    return JsonResponse(
        {
            "ok": True,
            "kind": kind,
        }
    )
