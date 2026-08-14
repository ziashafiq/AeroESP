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