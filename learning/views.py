from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
)
from django.db.models import Count, Q
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from .forms import LearningItemForm

from .models import (
    CourseModule,
    Enrollment,
    LearnerError,
    LearningCourse,
    LearningItem,
    LearningProgress,
    LearningProgram,
)


@login_required
def dashboard(request):

    programs = (
        LearningProgram.objects
        .filter(
            is_active=True,
        )
        .prefetch_related(
            "courses",
        )
        .order_by(
            "order",
        )
    )

    enrollments = (
        Enrollment.objects
        .filter(
            student=request.user,
            status=Enrollment.Status.ACTIVE,
        )
        .select_related(
            "course",
            "course__program",
        )
    )

    recent_items = (
        LearningItem.objects
        .filter(
            created_by=request.user,
        )
        .select_related(
            "module",
            "module__course",
        )
        .order_by(
            "-created_at",
        )[:5]
    )

    review_due_count = (
        LearningProgress.objects
        .filter(
            student=request.user,
            next_review_at__lte=timezone.now(),
        )
        .exclude(
            status=(
                LearningProgress.Status.MASTERED
            )
        )
        .count()
    )

    unresolved_errors = (
        LearnerError.objects
        .filter(
            student=request.user,
            resolved=False,
        )
        .count()
    )

    learned_count = (
        LearningItem.objects
        .filter(
            created_by=request.user,
        )
        .count()
    )

    context = {
        "programs": programs,
        "enrollments": enrollments,
        "recent_items": recent_items,
        "review_due_count": review_due_count,
        "unresolved_errors": unresolved_errors,
        "learned_count": learned_count,
    }

    return render(
        request,
        "learning/dashboard.html",
        context,
    )


@login_required
def my_courses(request):

    courses = (
        LearningCourse.objects
        .filter(
            is_active=True,
        )
        .select_related(
            "program",
        )
        .annotate(
            module_count=Count(
                "modules",
            )
        )
        .order_by(
            "program__order",
            "order",
        )
    )

    enrollments = {
        enrollment.course_id: enrollment
        for enrollment
        in Enrollment.objects
        .filter(
            student=request.user,
        )
        .select_related(
            "course",
        )
    }

    course_cards = []

    for course in courses:

        enrollment = (
            enrollments.get(
                course.pk
            )
        )

        course_cards.append(
            {
                "course": course,
                "enrollment": enrollment,
            }
        )

    return render(
        request,
        "learning/my_courses.html",
        {
            "course_cards": (
                course_cards
            ),
        },
    )


@login_required
def course_detail(
    request,
    pk,
):

    course = get_object_or_404(
        LearningCourse.objects
        .select_related(
            "program",
        )
        .prefetch_related(
            "modules",
            "modules__items",
        ),
        pk=pk,
        is_active=True,
    )

    enrollment = (
        Enrollment.objects
        .filter(
            student=request.user,
            course=course,
        )
        .first()
    )

    if request.method == "POST":

        if enrollment is None:

            Enrollment.objects.create(
                student=request.user,
                course=course,
            )

            messages.success(
                request,
                "Course added to My Courses.",
            )

        return redirect(
            "learning:course_detail",
            pk=course.pk,
        )

    return render(
        request,
        "learning/course_detail.html",
        {
            "course": course,
            "enrollment": enrollment,
        },
    )


@login_required
def learning_journal(
    request,
):

    query = (
        request.GET.get(
            "q",
            "",
        )
        .strip()
    )

    items = (
        LearningItem.objects
        .filter(
            created_by=request.user,
        )
        .select_related(
            "module",
            "module__course",
            "module__course__program",
        )
    )

    if query:

        items = items.filter(
            Q(
                title__icontains=query
            )
            | Q(
                definition_en__icontains=query
            )
            | Q(
                meaning_fa__icontains=query
            )
            | Q(
                example__icontains=query
            )
        )

    items = items.order_by(
        "-created_at"
    )

    return render(
        request,
        "learning/journal.html",
        {
            "items": items,
            "query": query,
        },
    )


@login_required
def learning_item_create(
    request,
):

    form = LearningItemForm(
        request.POST or None
    )

    if (
        request.method == "POST"
        and form.is_valid()
    ):

        item = form.save(
            commit=False
        )

        item.created_by = (
            request.user
        )

        item.save()

        messages.success(
            request,
            "Learning item saved.",
        )

        return redirect(
            "learning:learning_journal"
        )

    return render(
        request,
        "learning/item_form.html",
        {
            "form": form,
        },
    )


@login_required
def review_due(
    request,
):

    records = (
        LearningProgress.objects
        .filter(
            student=request.user,
            next_review_at__lte=timezone.now(),
        )
        .select_related(
            "learning_item",
            "learning_item__module",
        )
        .exclude(
            status=(
                LearningProgress.Status.MASTERED
            )
        )
        .order_by(
            "next_review_at",
        )
    )

    return render(
        request,
        "learning/review_due.html",
        {
            "records": records,
        },
    )


@login_required
def my_errors(
    request,
):

    errors = (
        LearnerError.objects
        .filter(
            student=request.user,
        )
        .select_related(
            "learning_item",
            "question",
        )
        .order_by(
            "-occurred_at",
        )
    )

    return render(
        request,
        "learning/errors.html",
        {
            "errors": errors,
        },
    )


def _build_course_dashboard(
    request,
    program_type,
):

    program = get_object_or_404(
        LearningProgram,
        program_type=program_type,
        is_active=True,
    )

    course = (
        LearningCourse.objects
        .filter(
            program=program,
            is_active=True,
        )
        .order_by("order")
        .first()
    )

    if course is None:
        return {
            "program": program,
            "course": None,
            "module_cards": [],
            "course_progress": 0,
            "total_items": 0,
            "mastered_items": 0,
        }

    modules = (
        course.modules
        .filter(
            is_active=True,
        )
        .order_by("order")
    )

    module_cards = []

    total_tracked = 0
    total_mastered = 0

    for module in modules:

        progress_qs = (
            LearningProgress.objects
            .filter(
                student=request.user,
                learning_item__module=module,
            )
        )

        tracked = progress_qs.count()

        mastered = (
            progress_qs
            .filter(
                status=(
                    LearningProgress
                    .Status
                    .MASTERED
                )
            )
            .count()
        )

        if tracked:
            progress_percent = round(
                mastered / tracked * 100
            )
        else:
            progress_percent = 0

        personal_items = (
            LearningItem.objects
            .filter(
                module=module,
                created_by=request.user,
            )
            .count()
        )

        public_items = (
            LearningItem.objects
            .filter(
                module=module,
                is_public=True,
            )
            .exclude(
                created_by=request.user,
            )
            .count()
        )

        module_cards.append(
            {
                "module": module,
                "tracked": tracked,
                "mastered": mastered,
                "progress_percent": progress_percent,
                "personal_items": personal_items,
                "public_items": public_items,
            }
        )

        total_tracked += tracked
        total_mastered += mastered

    if total_tracked:
        course_progress = round(
            total_mastered
            / total_tracked
            * 100
        )
    else:
        course_progress = 0

    return {
        "program": program,
        "course": course,
        "module_cards": module_cards,
        "course_progress": course_progress,
        "total_items": total_tracked,
        "mastered_items": total_mastered,
    }


@login_required
def ielts_dashboard(
    request,
):

    context = _build_course_dashboard(
        request,
        LearningProgram.ProgramType.IELTS,
    )

    context["dashboard_type"] = "IELTS"

    return render(
        request,
        "learning/program_dashboard.html",
        context,
    )


@login_required
def aerospace_dashboard(
    request,
):

    context = _build_course_dashboard(
        request,
        LearningProgram
        .ProgramType
        .AEROSPACE_ESP,
    )

    context["dashboard_type"] = "AEROSPACE"

    return render(
        request,
        "learning/program_dashboard.html",
        context,
    )


@login_required
def module_detail(
    request,
    module_id,
):

    module = get_object_or_404(
        CourseModule.objects
        .select_related(
            "course",
            "course__program",
        ),
        pk=module_id,
        is_active=True,
    )

    items = (
        LearningItem.objects
        .filter(
            module=module,
        )
        .filter(
            Q(created_by=request.user)
            | Q(is_public=True)
        )
        .distinct()
        .order_by("-created_at")
    )

    personal_count = (
        items
        .filter(
            created_by=request.user
        )
        .count()
    )

    progress_records = (
        LearningProgress.objects
        .filter(
            student=request.user,
            learning_item__module=module,
        )
    )

    tracked_count = (
        progress_records.count()
    )

    mastered_count = (
        progress_records
        .filter(
            status=(
                LearningProgress
                .Status
                .MASTERED
            )
        )
        .count()
    )

    if tracked_count:
        progress_percent = round(
            mastered_count
            / tracked_count
            * 100
        )
    else:
        progress_percent = 0

    return render(
        request,
        "learning/module_detail.html",
        {
            "module": module,
            "items": items,
            "personal_count": personal_count,
            "tracked_count": tracked_count,
            "mastered_count": mastered_count,
            "progress_percent": progress_percent,
        },
    )