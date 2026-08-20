from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import (
    login_required,
)
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from assessment.models import (
    AerospaceTopic,
    Question,
)

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
    PlacementAttempt,
    PlacementQuestion,
    PlacementResponse,
)


@login_required
def dashboard(request):
    # Enrollments
    general_enrollment = Enrollment.objects.filter(
        student=request.user,
        course__program__program_type=LearningProgram.ProgramType.IELTS,
        status=Enrollment.Status.ACTIVE
    ).first()

    aerospace_enrollment = Enrollment.objects.filter(
        student=request.user,
        course__program__program_type=LearningProgram.ProgramType.AEROSPACE_ESP,
        status=Enrollment.Status.ACTIVE
    ).first()

    # Progress per program
    def get_progress(program_type):
        qs = LearningProgress.objects.filter(
            student=request.user,
            learning_item__module__course__program__program_type=program_type
        )
        tracked = qs.count()
        mastered = qs.filter(status=LearningProgress.Status.MASTERED).count()
        return round(mastered / tracked * 100) if tracked else 0

    general_progress = get_progress(LearningProgram.ProgramType.IELTS)
    aerospace_progress = get_progress(LearningProgram.ProgramType.AEROSPACE_ESP)

    # Overall progress
    progress_qs = LearningProgress.objects.filter(student=request.user)
    due_review_count = progress_qs.filter(
        next_review_at__lte=timezone.now()
    ).exclude(
        status=LearningProgress.Status.MASTERED
    ).count()

    mastered_total = progress_qs.filter(
        status=LearningProgress.Status.MASTERED
    ).count()

    # Error analysis
    unresolved_errors = LearnerError.objects.filter(
        student=request.user,
        resolved=False,
    )

    weak_areas = (
        unresolved_errors
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total", "category")[:5]
    )

    recent_errors = (
        LearnerError.objects
        .filter(student=request.user)
        .select_related("learning_item", "question")
        .order_by("-occurred_at")[:5]
    )

    return render(
        request,
        "learning/dashboard.html",
        {
            "general_enrollment": general_enrollment,
            "aerospace_enrollment": aerospace_enrollment,
            "general_progress": general_progress,
            "aerospace_progress": aerospace_progress,
            "due_review_count": due_review_count,
            "mastered_total": mastered_total,
            "unresolved_error_count": unresolved_errors.count(),
            "weak_areas": weak_areas,
            "recent_errors": recent_errors,
        },
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
    topic = None

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

    topic_id = (
        request.GET.get("topic")
        or request.POST.get(
            "scope_topic"
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

    # If topic_id is provided, ensure it belongs to the module's domain
    if (
        topic_id
        and module is not None
        and module.aerospace_domain_id
    ):

        topic = get_object_or_404(
            AerospaceTopic,
            pk=topic_id,
            domain_id=module.aerospace_domain_id,
            is_active=True,
            approval_status__in=[
                AerospaceTopic.ApprovalStatus.CORE,
                AerospaceTopic.ApprovalStatus.APPROVED,
            ],
        )

    form = LearningItemForm(
        request.POST or None,
        course=course,
        module=module,
        topic=topic,
    )

    if (
        request.method == "POST"
        and form.is_valid()
    ):

        item = form.save(
            commit=False
        )

        # ==============================================
        # Automatically set aerospace domain/topic
        # based on the module's domain if applicable
        # ==============================================
        program_type = (
            item.module
            .course
            .program
            .program_type
        )

        if (
            program_type
            == "AEROSPACE_ESP"
        ):

            item.english_focus = ""
            item.english_topic = ""

            if (
                item.module
                .aerospace_domain_id
            ):

                item.aerospace_domain = (
                    item.module
                    .aerospace_domain
                )

            if topic is not None:
                item.aerospace_topic = topic

        else:

            item.aerospace_domain = None
            item.aerospace_topic = None

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

    # Determine scope title for display
    if topic is not None:

        scope_title = (
            f"{module.course.title} / "
            f"{module.title} / "
            f"{topic.name}"
        )

    elif module is not None:

        scope_title = (
            f"{module.course.title} / "
            f"{module.title}"
        )

    elif course is not None:

        scope_title = course.title

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
            "scope_topic_id": (
                topic.pk
                if topic
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


# =========================================================
# REVIEW QUEUE
# =========================================================

@login_required
def review_due(request):

    scope = (
        request.GET.get(
            "scope",
            "all",
        )
        .strip()
        .lower()
    )

    if scope not in {
        "all",
        "general",
        "aerospace",
    }:
        scope = "all"

    now = timezone.now()

    progress_qs = (
        LearningProgress.objects
        .filter(
            student=request.user,
        )
        .select_related(
            "learning_item",
            "learning_item__module",
        )
    )

    if scope == "general":

        progress_qs = progress_qs.filter(
            learning_item__module__course__program__program_type=(
                LearningProgram.ProgramType.IELTS
            )
        )

    elif scope == "aerospace":

        progress_qs = progress_qs.filter(
            learning_item__module__course__program__program_type=(
                LearningProgram.ProgramType.AEROSPACE_ESP
            )
        )

    due_items = (
        progress_qs
        .filter(
            next_review_at__lte=now,
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

    upcoming_items = (
        progress_qs
        .filter(
            next_review_at__gt=now,
        )
        .exclude(
            status=(
                LearningProgress.Status.MASTERED
            )
        )
        .order_by(
            "next_review_at",
        )[:10]
    )

    overdue_count = (
        due_items
        .filter(
            next_review_at__lt=(
                now
                - timedelta(days=1)
            )
        )
        .count()
    )

    mastered_count = (
        progress_qs
        .filter(
            status=(
                LearningProgress.Status.MASTERED
            )
        )
        .count()
    )

    return render(
        request,
        "learning/review_due.html",
        {
            "scope": scope,
            "due_items": due_items,
            "upcoming_items": upcoming_items,
            "due_count": due_items.count(),
            "overdue_count": overdue_count,
            "mastered_count": mastered_count,
        },
    )


# =========================================================
# ERROR ANALYSIS
# =========================================================

@login_required
def my_errors(request):

    scope = (
        request.GET.get(
            "scope",
            "all",
        )
        .strip()
        .lower()
    )

    if scope not in {
        "all",
        "general",
        "aerospace",
    }:
        scope = "all"

    errors = (
        LearnerError.objects
        .filter(
            student=request.user,
        )
        .select_related(
            "learning_item",
            "learning_item__module",
            "learning_item__module__course",
        )
    )

    if scope == "general":

        errors = errors.filter(
            is_general_english_error=True,
        )

    elif scope == "aerospace":

        errors = errors.filter(
            is_esp_specific_error=True,
        )

    category_summary = (
        errors
        .values(
            "category",
        )
        .annotate(
            total=Count("id"),
        )
        .order_by(
            "-total",
        )
    )

    unresolved = (
        errors
        .filter(
            resolved=False,
        )
    )

    return render(
        request,
        "learning/my_errors.html",
        {
            "scope": scope,
            "errors": errors[:100],
            "unresolved_count": unresolved.count(),
            "resolved_count": (
                errors
                .filter(
                    resolved=True,
                )
                .count()
            ),
            "general_count": (
                errors
                .filter(
                    is_general_english_error=True,
                )
                .count()
            ),
            "aerospace_count": (
                errors
                .filter(
                    is_esp_specific_error=True,
                )
                .count()
            ),
            "category_summary": category_summary,
        },
    )


@login_required
def resolve_learner_error(
    request,
    error_id,
):

    error = get_object_or_404(
        LearnerError,
        pk=error_id,
        student=request.user,
    )

    if request.method == "POST":

        error.resolved = True
        error.resolved_at = (
            timezone.now()
        )

        error.save(
            update_fields=[
                "resolved",
                "resolved_at",
            ]
        )

    return redirect(
        "learning:my_errors"
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


# =========================================================
# API: get aerospace topics for a given domain
# =========================================================

@login_required
def aerospace_topics_api(request):

    domain_id = request.GET.get(
        "domain"
    )

    if not domain_id:
        return JsonResponse(
            {
                "topics": [],
            }
        )

    topics = (
        AerospaceTopic.objects
        .filter(
            domain_id=domain_id,
            is_active=True,
            approval_status__in=[
                AerospaceTopic
                .ApprovalStatus
                .CORE,
                AerospaceTopic
                .ApprovalStatus
                .APPROVED,
            ],
        )
        .order_by(
            "order",
            "name",
        )
    )

    return JsonResponse(
        {
            "topics": [
                {
                    "id": topic.pk,
                    "name": topic.name,
                }
                for topic in topics
            ]
        }
    )


# =========================================================
# View: detail page for a specific aerospace topic
# =========================================================

@login_required
def aerospace_topic_detail(
    request,
    module_id,
    topic_id,
):

    module = get_object_or_404(
        CourseModule.objects
        .select_related(
            "course",
            "course__program",
            "aerospace_domain",
        ),
        pk=module_id,
        is_active=True,
    )

    topic = get_object_or_404(
        AerospaceTopic,
        pk=topic_id,
        is_active=True,
        approval_status__in=[
            AerospaceTopic.ApprovalStatus.CORE,
            AerospaceTopic.ApprovalStatus.APPROVED,
        ],
    )

    items = (
        LearningItem.objects
        .filter(
            module=module,
            aerospace_topic=topic,
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
            learning_item__aerospace_topic=topic,
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

    progress_percent = (
        round(
            mastered_count
            / tracked_count
            * 100
        )
        if tracked_count
        else 0
    )

    return render(
        request,
        "learning/aerospace_topic_detail.html",
        {
            "module": module,
            "topic": topic,
            "items": items,
            "personal_count": personal_count,
            "tracked_count": tracked_count,
            "mastered_count": mastered_count,
            "progress_percent": progress_percent,
        },
    )


# =========================================================
# Helper: map question skill to error category
# =========================================================

def _practice_error_category(
    question,
    learning_item,
):
    """
    Convert the question skill and program
    context into a LearnerError category.
    """

    skill = str(
        question.skill or ""
    ).upper()

    program_type = (
        learning_item
        .module
        .course
        .program
        .program_type
    )

    is_aerospace = (
        program_type
        == LearningProgram
        .ProgramType
        .AEROSPACE_ESP
    )

    if is_aerospace:

        if "READ" in skill:
            return (
                LearnerError
                .ErrorCategory
                .TECHNICAL_READING
            )

        if (
            "VOCAB" in skill
            or "TERM" in skill
        ):
            return (
                LearnerError
                .ErrorCategory
                .TECHNICAL_TERM
            )

    if "VOCAB" in skill:
        return (
            LearnerError
            .ErrorCategory
            .VOCABULARY
        )

    if "GRAMMAR" in skill:
        return (
            LearnerError
            .ErrorCategory
            .GRAMMAR
        )

    if "READ" in skill:
        return (
            LearnerError
            .ErrorCategory
            .READING
        )

    if "LISTEN" in skill:
        return (
            LearnerError
            .ErrorCategory
            .LISTENING
        )

    if "WRIT" in skill:
        return (
            LearnerError
            .ErrorCategory
            .WRITING
        )

    if "SPEAK" in skill:
        return (
            LearnerError
            .ErrorCategory
            .SPEAKING
        )

    return (
        LearnerError
        .ErrorCategory
        .OTHER
    )


def _question_option_text(
    question,
    answer_code,
):
    code = str(
        answer_code or ""
    ).strip().upper()

    options = {
        "A": question.option_a,
        "B": question.option_b,
        "C": question.option_c,
        "D": question.option_d,
    }

    return options.get(
        code,
        "",
    )


# =========================================================
# Daily Practice Views
# =========================================================

@login_required
def daily_practice(request):

    mode = (
        request.GET.get(
            "mode",
            "mixed",
        )
        .strip()
        .lower()
    )

    if mode not in {
        "general",
        "aerospace",
        "mixed",
    }:
        mode = "mixed"

    now = timezone.now()

    # Get all learning items with questions linked
    links = (
        LearningItemQuestion.objects
        .filter(
            learning_item__created_by=request.user,
        )
        .select_related(
            "learning_item",
            "learning_item__module",
            "question",
        )
        .order_by(
            "?",
        )
    )

    # Filter by mode
    if mode == "general":
        links = links.filter(
            learning_item__module__course__program__program_type=(
                LearningProgram.ProgramType.IELTS
            )
        )
    elif mode == "aerospace":
        links = links.filter(
            learning_item__module__course__program__program_type=(
                LearningProgram.ProgramType.AEROSPACE_ESP
            )
        )

    due_links = []
    future_links = []

    for link in links:
        progress = (
            LearningProgress.objects
            .filter(
                student=request.user,
                learning_item=link.learning_item,
            )
            .first()
        )

        if (
            progress is None
            or progress.next_review_at is None
            or progress.next_review_at <= now
        ):
            due_links.append(
                (
                    link,
                    progress,
                )
            )
        else:
            future_links.append(
                (
                    link,
                    progress,
                )
            )

    practice_pool = (
        due_links
        if due_links
        else future_links
    )

    current_link = None
    current_progress = None

    if practice_pool:
        current_link = practice_pool[0][0]
        current_progress = practice_pool[0][1]

    total_questions = links.count()
    due_count = len(due_links)

    context = {
        "mode": mode,
        "current_link": current_link,
        "current_progress": current_progress,
        "total_questions": total_questions,
        "due_count": due_count,
    }

    return render(
        request,
        "learning/daily_practice.html",
        context,
    )


@login_required
def practice_answer(
    request,
    link_id,
):

    link = get_object_or_404(
        LearningItemQuestion,
        pk=link_id,
        learning_item__created_by=request.user,
    )

    question = link.question
    learning_item = link.learning_item

    if request.method != "POST":
        return redirect(
            "learning:daily_practice"
        )

    selected_answer = (
        request.POST.get(
            "answer",
            "",
        )
        .strip()
        .upper()
    )

    correct_answer = (
        str(
            question.correct_answer
            or ""
        )
        .strip()
        .upper()
    )

    mode = (
        request.POST.get(
            "mode",
            "mixed",
        )
        .strip()
        .lower()
    )

    if mode not in {
        "general",
        "aerospace",
        "mixed",
    }:
        mode = "mixed"

    is_correct = (
        selected_answer == correct_answer
    )

    # Get or create progress record
    progress, created = (
        LearningProgress.objects
        .get_or_create(
            student=request.user,
            learning_item=learning_item,
            defaults={
                "status": LearningProgress.Status.LEARNING,
                "next_review_at": timezone.now()
                + timedelta(days=1),
            }
        )
    )

    # =============================================
    # Update progress based on answer
    # =============================================

    now = timezone.now()

    if is_correct:

        progress.correct_count += 1

        # Schedule using the CURRENT successful
        # review stage:
        # 1, 3, 7, 14, 30, 60 days.
        progress.schedule_next_review()

        progress.review_count += 1

    else:

        progress.incorrect_count += 1

        # Wrong answer resets the successful
        # spaced-repetition stage.
        progress.review_count = 0

        # Return the item for review tomorrow.
        progress.next_review_at = (
            now
            + timedelta(days=1)
        )

    total_attempts = (
        progress.correct_count
        + progress.incorrect_count
    )

    if total_attempts:

        progress.mastery_score = round(
            (
                progress.correct_count
                / total_attempts
            )
            * 100,
            2,
        )

    else:

        progress.mastery_score = 0

    mastery = float(
        progress.mastery_score
    )

    # =============================================
    # Learning Status
    # =============================================

    if not is_correct:

        progress.status = (
            LearningProgress
            .Status
            .REVIEW
        )

    elif (
        progress.correct_count >= 3
        and mastery >= 80
    ):

        progress.status = (
            LearningProgress
            .Status
            .MASTERED
        )

    elif total_attempts == 1:

        progress.status = (
            LearningProgress
            .Status
            .LEARNING
        )

    else:

        progress.status = (
            LearningProgress
            .Status
            .REVIEW
        )

    progress.last_reviewed_at = now
    progress.save()

    # Record the error if incorrect
    if not is_correct:

        program_type = (
            learning_item
            .module
            .course
            .program
            .program_type
        )

        is_aerospace = (
            program_type
            == LearningProgram
            .ProgramType
            .AEROSPACE_ESP
        )

        is_general = not is_aerospace

        LearnerError.objects.create(
            student=request.user,
            question=question,
            learning_item=learning_item,
            category=(
                _practice_error_category(
                    question,
                    learning_item,
                )
            ),
            student_response=(
                _question_option_text(
                    question,
                    selected_answer,
                )
            ),
            expected_response=(
                _question_option_text(
                    question,
                    correct_answer,
                )
            ),
            note=(
                "Automatically recorded "
                "from Daily Practice."
            ),
            is_general_english_error=(
                is_general
            ),
            is_esp_specific_error=(
                is_aerospace
            ),
        )

    return render(
        request,
        "learning/practice_feedback.html",
        {
            "link": link,
            "question": question,
            "learning_item": learning_item,
            "progress": progress,
            "selected_answer": (
                selected_answer
            ),
            "selected_answer_text": (
                _question_option_text(
                    question,
                    selected_answer,
                )
            ),
            "correct_answer": (
                correct_answer
            ),
            "correct_answer_text": (
                _question_option_text(
                    question,
                    correct_answer,
                )
            ),
            "is_correct": is_correct,
            "mode": mode,
        },
    )


# =========================================================
# Recovered learning views
# =========================================================

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
# Helper to build course dashboard (used above)
# =========================================================

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


# =========================================================
# Placement Test Helpers and Views
# =========================================================

PLACEMENT_SKILLS = (
    Question.Skill.VOCABULARY,
    Question.Skill.GRAMMAR,
    Question.Skill.READING,
    Question.Skill.LISTENING,
)


def _placement_level_from_score(
    score,
):
    """
    Internal development mapping.

    This is NOT an official IELTS-to-CEFR
    conversion.
    """

    value = float(
        score
    )

    if value < 30:
        return (
            "A1",
            Decimal("3.0"),
        )

    if value < 45:
        return (
            "A2",
            Decimal("4.0"),
        )

    if value < 60:
        return (
            "B1",
            Decimal("5.0"),
        )

    if value < 75:
        return (
            "B2",
            Decimal("6.0"),
        )

    if value < 90:
        return (
            "C1",
            Decimal("7.0"),
        )

    return (
        "C2",
        Decimal("8.0"),
    )


@login_required
def placement_test(request):
    """
    Show a page to choose which program to take the placement test for.
    """
    programs = LearningProgram.objects.filter(is_active=True)
    return render(
        request,
        "learning/placement_select.html",
        {"programs": programs},
    )


@login_required
def placement_test_start(
    request,
    program_type,
):

    program = get_object_or_404(
        LearningProgram,
        program_type=program_type,
        is_active=True,
    )

    # Check if there's an in-progress attempt
    attempt = (
        PlacementAttempt.objects
        .filter(
            student=request.user,
            program=program,
            status=PlacementAttempt.Status.IN_PROGRESS,
        )
        .first()
    )

    if attempt is None:
        # Create a new attempt
        attempt = PlacementAttempt.objects.create(
            student=request.user,
            program=program,
        )

        # Select questions for this attempt
        question_ids = (
            PlacementQuestion.objects
            .filter(
                program=program,
                is_active=True,
                question__status=Question.Status.APPROVED,
            )
            .values_list("question_id", flat=True)
            .order_by("order", "?")
        )

        # Shuffle and limit to e.g. 20 questions
        question_ids = list(question_ids)
        # We'll take up to 20 questions, ensuring we have some from each skill
        # For simplicity, we'll take the first 20 or all
        selected_ids = question_ids[:20]

        # Create placement responses for each question (empty, not answered yet)
        for q_id in selected_ids:
            question = Question.objects.get(pk=q_id)
            PlacementResponse.objects.create(
                attempt=attempt,
                question=question,
                selected_answer="",  # empty until answered
                correct_answer_snapshot=question.correct_answer or "",
                skill_snapshot=question.skill or "",
                is_correct=False,
            )

    # Get the first unanswered question (if any)
    next_response = (
        attempt.responses
        .filter(selected_answer="")
        .order_by("question_id")
        .first()
    )

    if next_response is None:
        # All questions answered? Then we should auto-submit? Or redirect to result.
        # For now, redirect to submit.
        return redirect(
            "learning:placement_test_submit",
            attempt_id=attempt.pk,
        )

    return render(
        request,
        "learning/placement_question.html",
        {
            "attempt": attempt,
            "response": next_response,
            "question": next_response.question,
            "total": attempt.responses.count(),
            "answered": attempt.responses.exclude(selected_answer="").count(),
        },
    )


@login_required
def placement_test_question(
    request,
    attempt_id,
):

    attempt = get_object_or_404(
        PlacementAttempt,
        pk=attempt_id,
        student=request.user,
        status=PlacementAttempt.Status.IN_PROGRESS,
    )

    # Get the first unanswered question
    next_response = (
        attempt.responses
        .filter(selected_answer="")
        .order_by("question_id")
        .first()
    )

    if next_response is None:
        # All answered, redirect to submit
        return redirect(
            "learning:placement_test_submit",
            attempt_id=attempt.pk,
        )

    if request.method == "POST":
        selected = request.POST.get("answer", "").strip().upper()
        if selected in ("A", "B", "C", "D"):
            next_response.selected_answer = selected
            next_response.is_correct = (
                selected == next_response.correct_answer_snapshot
            )
            next_response.answered_at = timezone.now()
            next_response.save()

            # Mark attempt as in progress (already)

            # Redirect to next question
            return redirect(
                "learning:placement_test_question",
                attempt_id=attempt.pk,
            )

    return render(
        request,
        "learning/placement_question.html",
        {
            "attempt": attempt,
            "response": next_response,
            "question": next_response.question,
            "total": attempt.responses.count(),
            "answered": attempt.responses.exclude(selected_answer="").count(),
        },
    )


@login_required
def placement_test_submit(
    request,
    attempt_id,
):

    attempt = get_object_or_404(
        PlacementAttempt,
        pk=attempt_id,
        student=request.user,
        status=PlacementAttempt.Status.IN_PROGRESS,
    )

    # Ensure all questions are answered
    unanswered = attempt.responses.filter(selected_answer="")
    if unanswered.exists():
        messages.warning(request, "Please answer all questions before submitting.")
        return redirect(
            "learning:placement_test_question",
            attempt_id=attempt.pk,
        )

    # Compute scores
    responses = attempt.responses.all()
    total = responses.count()

    # Skill breakdown
    skills = {}
    for skill in PLACEMENT_SKILLS:
        skill_responses = responses.filter(skill_snapshot=skill)
        total_skill = skill_responses.count()
        correct_skill = skill_responses.filter(is_correct=True).count()
        score = (correct_skill / total_skill * 100) if total_skill else 0
        skills[skill] = score

    vocabulary_score = skills.get(Question.Skill.VOCABULARY, 0)
    grammar_score = skills.get(Question.Skill.GRAMMAR, 0)
    reading_score = skills.get(Question.Skill.READING, 0)
    listening_score = skills.get(Question.Skill.LISTENING, 0)

    # Overall score (average of skill scores)
    overall_score = (
        vocabulary_score + grammar_score + reading_score + listening_score
    ) / 4

    # Determine level
    cefr_level, ielts_estimate = _placement_level_from_score(
        overall_score
    )

    attempt.vocabulary_score = vocabulary_score
    attempt.grammar_score = grammar_score
    attempt.reading_score = reading_score
    attempt.listening_score = listening_score
    attempt.overall_score = overall_score
    attempt.cefr_level = cefr_level
    attempt.ielts_estimate = ielts_estimate
    attempt.status = PlacementAttempt.Status.COMPLETED
    attempt.completed_at = timezone.now()
    attempt.save()

    # Update enrollment
    program = attempt.program
    course = (
        program.courses
        .filter(is_active=True)
        .order_by("order", "pk")
        .first()
    )

    if course is not None:
        enrollment, _ = Enrollment.objects.get_or_create(
            student=request.user,
            course=course,
        )
        enrollment.status = Enrollment.Status.ACTIVE
        enrollment.assigned_level = cefr_level
        enrollment.placement_status = Enrollment.PlacementStatus.PLACEMENT_TEST
        enrollment.placement_updated_at = timezone.now()
        enrollment.save()

    return redirect(
        "learning:placement_result",
        attempt_id=attempt.pk,
    )


@login_required
def placement_result(
    request,
    attempt_id,
):

    attempt = get_object_or_404(
        PlacementAttempt.objects
        .select_related(
            "program",
        ),
        pk=attempt_id,
        student=request.user,
        status=(
            PlacementAttempt
            .Status
            .COMPLETED
        ),
    )

    responses = (
        attempt.responses
        .select_related(
            "question",
        )
        .order_by(
            "question__skill",
            "question_id",
        )
    )

    correct_count = (
        responses
        .filter(
            is_correct=True,
        )
        .count()
    )

    total_count = (
        responses.count()
    )

    return render(
        request,
        "learning/placement_result.html",
        {
            "attempt": attempt,
            "responses": responses,
            "correct_count": (
                correct_count
            ),
            "total_count": (
                total_count
            ),
        },
    )