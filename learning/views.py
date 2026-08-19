from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
)
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from assessment.models import Question

from .forms import (
    LearningItemForm,
    LearningQuestionForm,
)

from .models import (
    CourseModule,
    Enrollment,
    LearnerError,
    LearningCourse,
    LearningItem,
    LearningItemQuestion,
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

    module = None
    course = None

    module_id = (
        request.GET.get("module")
        or request.POST.get(
            "scope_module"
        )
    )

    course_id = (
        request.GET.get("course")
        or request.POST.get(
            "scope_course"
        )
    )

    if module_id:

        module = (
            CourseModule.objects
            .filter(
                pk=module_id,
                is_active=True,
                course__is_active=True,
                course__program__is_active=True,
            )
            .select_related(
                "course",
                "course__program",
            )
            .first()
        )

        if module is not None:
            course = module.course

    elif course_id:

        course = (
            LearningCourse.objects
            .filter(
                pk=course_id,
                is_active=True,
                program__is_active=True,
            )
            .select_related(
                "program",
            )
            .first()
        )

    form = LearningItemForm(
        request.POST or None,
        course=course,
        module=module,
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
            "learning:module_detail",
            module_id=item.module_id,
        )

    if module is not None:

        scope_title = (
            f"{module.course.title} "
            f"/ {module.title}"
        )

    elif course is not None:

        scope_title = (
            course.title
        )

    else:

        scope_title = (
            "All Learning Programs"
        )

    return render(
        request,
        "learning/item_form.html",
        {
            "form": form,
            "scope_course_id": (
                course.pk
                if course
                else ""
            ),
            "scope_module_id": (
                module.pk
                if module
                else ""
            ),
            "scope_title": (
                scope_title
            ),
            "locked_module": (
                module is not None
            ),
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
            "enrollment": None,
            "module_cards": [],
            "course_progress": 0,
            "total_items": 0,
            "mastered_items": 0,
        }

    enrollment = (
        Enrollment.objects
        .filter(
            student=request.user,
            course=course,
        )
        .first()
    )

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

        progress_percent = (
            round(
                mastered
                / tracked
                * 100
            )
            if tracked
            else 0
        )

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
                "progress_percent": (
                    progress_percent
                ),
                "personal_items": (
                    personal_items
                ),
                "public_items": (
                    public_items
                ),
            }
        )

        total_tracked += tracked
        total_mastered += mastered

    course_progress = (
        round(
            total_mastered
            / total_tracked
            * 100
        )
        if total_tracked
        else 0
    )

    return {
        "program": program,
        "course": course,
        "enrollment": enrollment,
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


# =========================================================
# Helper: infer skill from learning item
# =========================================================

def _infer_question_skill(
    learning_item,
):

    module_title = (
        learning_item.module.title
        .strip()
        .lower()
    )

    if "vocab" in module_title:
        return Question.Skill.VOCABULARY

    if "grammar" in module_title:
        return Question.Skill.GRAMMAR

    if "listen" in module_title:
        return Question.Skill.LISTENING

    if "writing" in module_title:
        return Question.Skill.WRITING

    if "speaking" in module_title:
        return Question.Skill.SPEAKING

    if "reading" in module_title:
        return Question.Skill.READING

    return Question.Skill.READING


# =========================================================
# Create a practice question from a learning item
# =========================================================

@login_required
def create_practice_question(
    request,
    learning_item_id,
):

    learning_item = get_object_or_404(
        LearningItem,
        pk=learning_item_id,
        created_by=request.user,
    )

    # GET: show form
    if request.method != "POST":
        form = LearningQuestionForm(
            learning_item=learning_item,
        )
        return render(
            request,
            "learning/question_form.html",
            {
                "form": form,
                "learning_item": learning_item,
            },
        )

    # POST: process form
    form = LearningQuestionForm(
        request.POST,
        learning_item=learning_item,
    )

    if not form.is_valid():
        return render(
            request,
            "learning/question_form.html",
            {
                "form": form,
                "learning_item": learning_item,
            },
        )

    # Create the question
    question = form.save(commit=False)

    # Set track based on program type
    program_type = (
        learning_item
        .module
        .course
        .program
        .program_type
    )

    if program_type == "IELTS":
        question.track = (
            Question.Track.GENERAL_ENGLISH
        )
        question.domain_ref = None
        question.topic_ref = None
        question.aerospace_domain = ""
    else:
        question.track = (
            Question.Track.AEROSPACE_ESP
        )

    question.skill = (
        _infer_question_skill(
            learning_item
        )
    )

    question.owner = None
    question.question_language = (
        Question.Language.ENGLISH
    )
    question.options_language = (
        Question.Language.ENGLISH
    )
    question.source_type = (
        Question.SourceType.MANUAL
    )
    question.source_reference = (
        f"Learning Item #{learning_item.pk}"
    )
    question.status = (
        Question.Status.DRAFT
    )
    question.visibility = (
        Question.Visibility.PRIVATE
    )

    question.full_clean()
    question.save()

    # Link to the learning item
    LearningItemQuestion.objects.create(
        learning_item=learning_item,
        question=question,
    )

    messages.success(
        request,
        "Practice question created.",
    )

    return redirect(
        "learning:module_detail",
        module_id=(
            learning_item.module_id
        ),
    )