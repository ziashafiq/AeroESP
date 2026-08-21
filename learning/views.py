from datetime import timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import (
    login_required,
)
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.http import Http404, JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from accounts.decorators import approved_teacher_required

from assessment.models import (
    AerospaceTopic,
    Question,
)

from .forms import (
    LearningItemForm,
    LearningQuestionForm,
    ResourceForm,
)

from .models import (
    CourseModule,
    Enrollment,
    LearnerError,
    LearningCourse,
    LearningEvent,
    LearningItem,
    LearningItemQuestion,
    LearningProgress,
    LearningProgram,
    PlacementAttempt,
    PlacementQuestion,
    PlacementResponse,
    Resource,
)


# =========================================================
# Helper: require approved teacher or superuser
# =========================================================

def _require_learning_teacher(user):
    if user.is_superuser:
        return
    profile = getattr(user, "teacher_profile", None)
    if profile is None or not profile.is_approved:
        raise PermissionDenied("You are not an approved teacher.")


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

        # ==============================================
        # Record error resolution event
        # ==============================================
        _record_learning_event(
            student=request.user,
            event_type=(
                LearningEvent
                .EventType
                .ERROR_RESOLVED
            ),
            learning_item=(
                error.learning_item
            ),
            question=(
                error.question
            ),
            metadata={
                "error_category": (
                    error.category
                ),
                "error_id": error.pk,
            },
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
# Helper: record a learning event
# =========================================================

def _record_learning_event(
    student,
    event_type,
    learning_item=None,
    question=None,
    placement_attempt=None,
    selected_answer="",
    correct_answer="",
    is_correct=None,
    mastery_before=None,
    mastery_after=None,
    review_count_before=None,
    review_count_after=None,
    metadata=None,
):
    """
    Record a learning event for analytics.
    """
    program_type = ""
    skill = ""
    aerospace_domain = ""
    aerospace_topic = ""
    english_focus = ""
    english_topic = ""

    if learning_item is not None:
        program_type = (
            learning_item
            .module
            .course
            .program
            .program_type
        )
        if learning_item.aerospace_domain:
            aerospace_domain = (
                learning_item
                .aerospace_domain
                .name
            )
        if learning_item.aerospace_topic:
            aerospace_topic = (
                learning_item
                .aerospace_topic
                .name
            )
        english_focus = (
            learning_item.english_focus
            or ""
        )
        english_topic = (
            learning_item.english_topic
            or ""
        )

    if question is not None:
        skill = (
            question.skill
            or ""
        )

    return LearningEvent.objects.create(
        student=student,
        event_type=event_type,
        learning_item=learning_item,
        question=question,
        placement_attempt=placement_attempt,
        program_type=program_type,
        skill=skill,
        aerospace_domain=aerospace_domain,
        aerospace_topic=aerospace_topic,
        english_focus=english_focus,
        english_topic=english_topic,
        selected_answer=selected_answer,
        correct_answer=correct_answer,
        is_correct=is_correct,
        mastery_before=mastery_before,
        mastery_after=mastery_after,
        review_count_before=review_count_before,
        review_count_after=review_count_after,
        metadata=metadata or {},
    )


# =========================================================
# Adaptive Practice Helpers
# =========================================================

def _build_adaptive_practice_pool(user, mode):
    """
    Build a list of candidate practice items (LearningItemQuestion) for the user,
    categorized into buckets: weak, due, new, reinforcement.
    Returns a list of dictionaries with keys: link, progress, bucket, score, unresolved_errors.
    """
    now = timezone.now()

    # Base queryset: all questions linked to learning items created by the user
    qs = LearningItemQuestion.objects.filter(
        learning_item__created_by=user
    ).select_related(
        "learning_item",
        "learning_item__module",
        "question",
    )

    # Filter by mode (general / aerospace / mixed)
    if mode == "general":
        qs = qs.filter(
            learning_item__module__course__program__program_type=LearningProgram.ProgramType.IELTS
        )
    elif mode == "aerospace":
        qs = qs.filter(
            learning_item__module__course__program__program_type=LearningProgram.ProgramType.AEROSPACE_ESP
        )
    # else: mixed, no filter

    candidates = []

    for link in qs:
        # Get or create progress for this user and learning item
        progress, _ = LearningProgress.objects.get_or_create(
            student=user,
            learning_item=link.learning_item,
            defaults={
                "status": LearningProgress.Status.NEW,
                "next_review_at": None,
            }
        )

        # Skip mastered items
        if progress.status == LearningProgress.Status.MASTERED:
            continue

        # Count unresolved errors for this learning item
        unresolved_errors = LearnerError.objects.filter(
            student=user,
            learning_item=link.learning_item,
            resolved=False
        ).count()

        # Determine bucket
        bucket = None
        score = 0

        if unresolved_errors > 0:
            bucket = "weak"
            score = 100 + unresolved_errors  # higher score for more errors
        elif progress.next_review_at and progress.next_review_at <= now:
            bucket = "due"
            score = 80
        elif progress.status == LearningProgress.Status.NEW or progress.review_count == 0:
            bucket = "new"
            score = 60
        else:
            # Reinforcement: has been reviewed but not mastered, and not due yet
            bucket = "reinforcement"
            mastery = float(progress.mastery_score or 0)
            score = max(0, 100 - mastery)

        candidates.append({
            "link": link,
            "progress": progress,
            "bucket": bucket,
            "score": score,
            "unresolved_errors": unresolved_errors,
        })

    return candidates


def _select_adaptive_question(request, mode):
    """
    Selects the most appropriate question from the practice pool using adaptive logic.
    Returns a tuple (selected_candidate_dict, reason_label).
    """
    candidates = _build_adaptive_practice_pool(request.user, mode)

    if not candidates:
        return None, None

    # Get recently practiced links from session to avoid repetition
    recent_ids = request.session.get("practice_recent_links", [])
    # Filter out recently practiced (unless we have very few)
    available = [c for c in candidates if c["link"].pk not in recent_ids]

    if not available:
        # If all are recent, just use all candidates
        available = candidates
        recent_ids = []  # reset recent list

    # Determine preferred bucket based on sequence slot
    sequence = int(request.session.get("practice_sequence", 0))
    slot = sequence % 10

    # Bucket preference order: weak -> due -> new -> reinforcement
    if slot <= 3:
        preferred_bucket = "weak"
    elif slot <= 6:
        preferred_bucket = "due"
    elif slot <= 8:
        preferred_bucket = "new"
    else:
        preferred_bucket = "reinforcement"

    preferred = [c for c in available if c["bucket"] == preferred_bucket]
    pool = preferred if preferred else available

    # Select the candidate with highest score (and tie-break by newer pk)
    selected = max(pool, key=lambda item: (item["score"], -item["link"].pk))

    # Update session
    selected_id = selected["link"].pk
    recent_ids.append(selected_id)
    request.session["practice_recent_links"] = recent_ids[-5:]  # keep last 5
    request.session["practice_sequence"] = sequence + 1

    reason_labels = {
        "weak": "Weak Area",
        "due": "Due Review",
        "new": "New Content",
        "reinforcement": "Retention Practice",
    }

    return selected, reason_labels.get(selected["bucket"], "Practice")


# =========================================================
# Daily Practice View (Adaptive)
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

    candidates = _build_adaptive_practice_pool(request.user, mode)
    selected, selection_reason = _select_adaptive_question(request, mode)

    current_link = selected["link"] if selected else None
    current_progress = selected["progress"] if selected else None

    due_count = sum(1 for item in candidates if item["bucket"] == "due")
    weak_count = sum(1 for item in candidates if item["bucket"] == "weak")
    new_count = sum(1 for item in candidates if item["bucket"] == "new")

    return render(
        request,
        "learning/daily_practice.html",
        {
            "mode": mode,
            "current_link": current_link,
            "current_progress": current_progress,
            "total_questions": len(candidates),
            "due_count": due_count,
            "weak_count": weak_count,
            "new_count": new_count,
            "selection_reason": selection_reason,
        },
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

    # Capture before values for event logging
    mastery_before = progress.mastery_score
    review_count_before = progress.review_count

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

    # =============================================
    # Record learning event
    # =============================================
    _record_learning_event(
        student=request.user,
        event_type=(
            LearningEvent
            .EventType
            .PRACTICE_ANSWER
        ),
        learning_item=learning_item,
        question=question,
        selected_answer=selected_answer,
        correct_answer=correct_answer,
        is_correct=is_correct,
        mastery_before=mastery_before,
        mastery_after=progress.mastery_score,
        review_count_before=review_count_before,
        review_count_after=progress.review_count,
        metadata={
            "practice_mode": mode,
            "progress_status": (
                progress.status
            ),
            "next_review_at": (
                progress.next_review_at.isoformat()
                if progress.next_review_at
                else None
            ),
        },
    )

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


def _course_level_from_cefr(
    cefr_level,
):
    mapping = {
        "A1": (
            LearningCourse.Level.BEGINNER
        ),
        "A2": (
            LearningCourse.Level.ELEMENTARY
        ),
        "B1": (
            LearningCourse.Level.INTERMEDIATE
        ),
        "B2": (
            LearningCourse.Level.UPPER_INTERMEDIATE
        ),
        "C1": (
            LearningCourse.Level.ADVANCED
        ),
        "C2": (
            LearningCourse.Level.ADVANCED
        ),
    }

    return mapping.get(
        str(cefr_level).strip().upper(),
        "",
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

    # ==========================================
    # Record placement completion event
    # ==========================================
    _record_learning_event(
        student=request.user,
        event_type=(
            LearningEvent
            .EventType
            .PLACEMENT_COMPLETE
        ),
        placement_attempt=attempt,
        metadata={
            "overall_score": (
                str(
                    attempt.overall_score
                )
            ),
            "cefr_level": (
                attempt.cefr_level
            ),
            "ielts_estimate": (
                str(
                    attempt.ielts_estimate
                )
                if attempt.ielts_estimate
                is not None
                else None
            ),
            "vocabulary_score": (
                str(
                    attempt.vocabulary_score
                )
            ),
            "grammar_score": (
                str(
                    attempt.grammar_score
                )
            ),
            "reading_score": (
                str(
                    attempt.reading_score
                )
            ),
            "listening_score": (
                str(
                    attempt.listening_score
                )
            ),
        },
    )

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
        enrollment.assigned_level = _course_level_from_cefr(cefr_level)
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


# =========================================================
# Learning Path Recommendations
# =========================================================

@login_required
def learning_path(request):

    general_candidates = (
        _build_adaptive_practice_pool(
            request.user,
            "general",
        )
    )

    aerospace_candidates = (
        _build_adaptive_practice_pool(
            request.user,
            "aerospace",
        )
    )

    def top_items(
        candidates,
        limit=8,
    ):
        return sorted(
            candidates,
            key=lambda item: (
                item["score"],
                item["unresolved_errors"],
            ),
            reverse=True,
        )[:limit]

    general_recommendations = (
        top_items(
            general_candidates
        )
    )

    aerospace_recommendations = (
        top_items(
            aerospace_candidates
        )
    )

    latest_placement = (
        PlacementAttempt.objects
        .filter(
            student=request.user,
            status=(
                PlacementAttempt
                .Status
                .COMPLETED
            ),
        )
        .order_by(
            "-completed_at"
        )
        .first()
    )

    return render(
        request,
        "learning/learning_path.html",
        {
            "general_recommendations": (
                general_recommendations
            ),
            "aerospace_recommendations": (
                aerospace_recommendations
            ),
            "latest_placement": (
                latest_placement
            ),
        },
    )


# =========================================================
# Learning Analytics
# =========================================================

@login_required
def learning_analytics(request):
    now = timezone.now()

    progress_qs = (
        LearningProgress.objects
        .filter(
            student=request.user,
        )
        .select_related(
            "learning_item",
            "learning_item__module",
            "learning_item__module__course",
            "learning_item__module__course__program",
            "learning_item__aerospace_domain",
            "learning_item__aerospace_topic",
        )
    )

    # ==========================================
    # Overall statistics
    # ==========================================

    total_correct = sum(
        p.correct_count
        for p in progress_qs
    )

    total_incorrect = sum(
        p.incorrect_count
        for p in progress_qs
    )

    total_attempts = (
        total_correct
        + total_incorrect
    )

    overall_accuracy = (
        round(
            total_correct
            / total_attempts
            * 100,
            1,
        )
        if total_attempts
        else 0
    )

    tracked_count = (
        progress_qs.count()
    )

    mastered_count = (
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

    mastery_percent = (
        round(
            mastered_count
            / tracked_count
            * 100,
            1,
        )
        if tracked_count
        else 0
    )

    due_count = (
        progress_qs
        .filter(
            next_review_at__lte=now,
        )
        .exclude(
            status=(
                LearningProgress
                .Status
                .MASTERED
            )
        )
        .count()
    )

    # ==========================================
    # Program statistics
    # ==========================================

    def program_stats(
        program_type,
    ):

        qs = progress_qs.filter(
            learning_item__module__course__program__program_type=(
                program_type
            )
        )

        correct = sum(
            p.correct_count
            for p in qs
        )

        incorrect = sum(
            p.incorrect_count
            for p in qs
        )

        attempts = (
            correct + incorrect
        )

        tracked = qs.count()

        mastered = (
            qs.filter(
                status=(
                    LearningProgress
                    .Status
                    .MASTERED
                )
            )
            .count()
        )

        return {
            "correct": correct,
            "incorrect": incorrect,
            "attempts": attempts,
            "accuracy": (
                round(
                    correct
                    / attempts
                    * 100,
                    1,
                )
                if attempts
                else 0
            ),
            "tracked": tracked,
            "mastered": mastered,
            "mastery": (
                round(
                    mastered
                    / tracked
                    * 100,
                    1,
                )
                if tracked
                else 0
            ),
        }

    general_stats = program_stats(
        LearningProgram
        .ProgramType
        .IELTS
    )

    aerospace_stats = program_stats(
        LearningProgram
        .ProgramType
        .AEROSPACE_ESP
    )

    # ==========================================
    # Error distribution
    # ==========================================

    error_qs = (
        LearnerError.objects
        .filter(
            student=request.user,
        )
    )

    error_distribution = (
        error_qs
        .values(
            "category",
        )
        .annotate(
            total=Count("id"),
        )
        .order_by(
            "-total",
            "category",
        )
    )

    unresolved_distribution = (
        error_qs
        .filter(
            resolved=False,
        )
        .values(
            "category",
        )
        .annotate(
            total=Count("id"),
        )
        .order_by(
            "-total",
            "category",
        )[:10]
    )

    # ==========================================
    # Aerospace Domain statistics
    # ==========================================

    domain_data = {}

    aerospace_progress = (
        progress_qs
        .filter(
            learning_item__module__course__program__program_type=(
                LearningProgram
                .ProgramType
                .AEROSPACE_ESP
            )
        )
    )

    for progress in aerospace_progress:

        item = progress.learning_item

        if item.aerospace_domain:

            key = (
                item.aerospace_domain.name
            )

        else:

            key = (
                item.module.title
            )

        data = domain_data.setdefault(
            key,
            {
                "name": key,
                "correct": 0,
                "incorrect": 0,
                "tracked": 0,
                "mastered": 0,
            },
        )

        data["correct"] += (
            progress.correct_count
        )

        data["incorrect"] += (
            progress.incorrect_count
        )

        data["tracked"] += 1

        if (
            progress.status
            == LearningProgress
            .Status
            .MASTERED
        ):
            data["mastered"] += 1

    domain_stats = []

    for data in domain_data.values():

        attempts = (
            data["correct"]
            + data["incorrect"]
        )

        data["accuracy"] = (
            round(
                data["correct"]
                / attempts
                * 100,
                1,
            )
            if attempts
            else 0
        )

        data["mastery"] = (
            round(
                data["mastered"]
                / data["tracked"]
                * 100,
                1,
            )
            if data["tracked"]
            else 0
        )

        domain_stats.append(
            data
        )

    domain_stats.sort(
        key=lambda x: (
            x["accuracy"],
            x["name"],
        )
    )

    # ==========================================
    # Aerospace Topic statistics
    # ==========================================

    topic_data = {}

    for progress in aerospace_progress:

        topic = (
            progress
            .learning_item
            .aerospace_topic
        )

        if topic is None:
            continue

        key = topic.name

        data = topic_data.setdefault(
            key,
            {
                "name": key,
                "correct": 0,
                "incorrect": 0,
                "tracked": 0,
            },
        )

        data["correct"] += (
            progress.correct_count
        )

        data["incorrect"] += (
            progress.incorrect_count
        )

        data["tracked"] += 1

    topic_stats = []

    for data in topic_data.values():

        attempts = (
            data["correct"]
            + data["incorrect"]
        )

        data["accuracy"] = (
            round(
                data["correct"]
                / attempts
                * 100,
                1,
            )
            if attempts
            else 0
        )

        topic_stats.append(
            data
        )

    topic_stats.sort(
        key=lambda x: (
            x["accuracy"],
            x["name"],
        )
    )

    # ==========================================
    # Placement
    # ==========================================

    latest_placement = (
        PlacementAttempt.objects
        .filter(
            student=request.user,
            status=(
                PlacementAttempt
                .Status
                .COMPLETED
            ),
        )
        .order_by(
            "-completed_at",
        )
        .first()
    )

    return render(
        request,
        "learning/analytics.html",
        {
            "overall_accuracy": (
                overall_accuracy
            ),
            "tracked_count": (
                tracked_count
            ),
            "mastered_count": (
                mastered_count
            ),
            "mastery_percent": (
                mastery_percent
            ),
            "due_count": (
                due_count
            ),
            "total_attempts": (
                total_attempts
            ),
            "general_stats": (
                general_stats
            ),
            "aerospace_stats": (
                aerospace_stats
            ),
            "error_distribution": (
                error_distribution
            ),
            "unresolved_distribution": (
                unresolved_distribution
            ),
            "domain_stats": (
                domain_stats
            ),
            "topic_stats": (
                topic_stats
            ),
            "latest_placement": (
                latest_placement
            ),
        },
    )


# =========================================================
# Teacher Learning Views
# =========================================================

def _student_course_summary(student, course):
    """
    Compute summary statistics for a student in a specific course.
    Returns a dict with correct, incorrect, attempts, accuracy,
    tracked, mastered, mastery, due, errors, needs_attention.
    """
    now = timezone.now()

    progress_qs = LearningProgress.objects.filter(
        student=student,
        learning_item__module__course=course,
    )

    correct = sum(p.correct_count for p in progress_qs)
    incorrect = sum(p.incorrect_count for p in progress_qs)
    attempts = correct + incorrect
    tracked = progress_qs.count()
    mastered = progress_qs.filter(status=LearningProgress.Status.MASTERED).count()

    accuracy = round(correct / attempts * 100, 1) if attempts else 0
    mastery = round(mastered / tracked * 100, 1) if tracked else 0

    due = progress_qs.filter(
        next_review_at__lte=now,
    ).exclude(
        status=LearningProgress.Status.MASTERED
    ).count()

    errors = LearnerError.objects.filter(
        student=student,
        learning_item__module__course=course,
        resolved=False,
    ).count()

    needs_attention = (
        (attempts >= 3 and accuracy < 60) or
        errors >= 3 or
        due >= 5
    )

    return {
        "correct": correct,
        "incorrect": incorrect,
        "attempts": attempts,
        "accuracy": accuracy,
        "tracked": tracked,
        "mastered": mastered,
        "mastery": mastery,
        "due": due,
        "errors": errors,
        "needs_attention": needs_attention,
    }


@login_required
def teacher_learning_dashboard(request):
    """
    Dashboard for approved teachers to monitor student progress.
    """
    _require_learning_teacher(request.user)

    # Get all courses taught by this teacher
    courses = LearningCourse.objects.filter(
        created_by=request.user,
        is_active=True,
    ).select_related('program')

    course_ids = list(courses.values_list('id', flat=True))
    if not course_ids:
        # No courses - return empty dashboard
        return render(
            request,
            "learning/teacher_learning_dashboard.html",
            {
                "courses": [],
                "classes": [],
                "course_count": 0,
                "class_count": 0,
                "student_count": 0,
                "weak_categories": [],
                "attention_students": [],
            }
        )

    # Get all enrollments for these courses (active status)
    enrollments = Enrollment.objects.filter(
        course_id__in=course_ids,
        status=Enrollment.Status.ACTIVE,
    ).select_related('student', 'course')

    # Group by class_name (or "Unassigned" for blank)
    classes = {}
    unique_students = set()

    for enrollment in enrollments:
        class_name = enrollment.class_name or "Unassigned"
        key = (enrollment.course_id, class_name)
        if key not in classes:
            classes[key] = {
                "course": enrollment.course,
                "class_name": class_name,
                "students": [],
            }
        # Avoid duplicates (a student might be enrolled in multiple courses)
        # We'll add a placeholder; later we compute summary per student per course
        # Actually we want per student per course, so we keep all.
        student_id = enrollment.student_id
        unique_students.add(student_id)
        classes[key]["students"].append(enrollment.student)

    # For each class group, compute per-student summaries
    class_list = []
    for (course_id, class_name), group in classes.items():
        student_rows = []
        for student in group["students"]:
            summary = _student_course_summary(student, group["course"])
            student_rows.append({
                "student": student,
                "summary": summary,
            })
        # Sort students by needs_attention first, then by accuracy ascending
        student_rows.sort(
            key=lambda row: (
                not row["summary"]["needs_attention"],  # True first
                row["summary"]["accuracy"],
            )
        )
        class_list.append({
            "course": group["course"],
            "class_name": class_name,
            "students": student_rows,
        })

    # Top weak categories across all classes
    weak_categories = (
        LearnerError.objects
        .filter(
            student_id__in=unique_students,
            learning_item__module__course_id__in=course_ids,
            resolved=False,
        )
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total", "category")[:8]
    )

    # Students needing attention
    attention_students = []
    for group in class_list:
        for row in group["students"]:
            if row["summary"]["needs_attention"]:
                attention_students.append({
                    "student": row["student"],
                    "course": group["course"],
                    "class_name": group["class_name"],
                    "summary": row["summary"],
                })

    attention_students.sort(
        key=lambda row: (
            row["summary"]["accuracy"],
            -row["summary"]["errors"],
        )
    )

    return render(
        request,
        "learning/teacher_learning_dashboard.html",
        {
            "courses": courses,
            "classes": class_list,
            "course_count": len(courses),
            "class_count": len(class_list),
            "student_count": len(unique_students),
            "weak_categories": weak_categories,
            "attention_students": attention_students[:20],
        },
    )


@login_required
def teacher_class_detail(request, course_id, class_name):
    """
    Detailed view for a specific class within a course.
    """
    _require_learning_teacher(request.user)

    course = get_object_or_404(
        LearningCourse.objects.select_related('program'),
        pk=course_id,
        created_by=request.user,
        is_active=True,
    )

    # Get enrollments for this course and class
    class_name = class_name if class_name != "Unassigned" else ""
    enrollments = Enrollment.objects.filter(
        course=course,
        class_name=class_name,
        status=Enrollment.Status.ACTIVE,
    ).select_related('student')

    if not enrollments:
        # No students in this class
        return render(
            request,
            "learning/teacher_class_detail.html",
            {
                "course": course,
                "class_name": class_name or "Unassigned",
                "students": [],
                "student_count": 0,
                "class_accuracy": 0,
                "class_mastery": 0,
                "weak_categories": [],
                "domain_stats": [],
            }
        )

    students = []
    total_correct = 0
    total_incorrect = 0
    total_tracked = 0
    total_mastered = 0
    student_ids = []

    for enrollment in enrollments:
        student = enrollment.student
        student_ids.append(student.id)
        summary = _student_course_summary(student, course)
        students.append({
            "student": student,
            "summary": summary,
        })
        total_correct += summary["correct"]
        total_incorrect += summary["incorrect"]
        total_tracked += summary["tracked"]
        total_mastered += summary["mastered"]

    # Class-wide accuracy and mastery
    total_attempts = total_correct + total_incorrect
    class_accuracy = round(total_correct / total_attempts * 100, 1) if total_attempts else 0
    class_mastery = round(total_mastered / total_tracked * 100, 1) if total_tracked else 0

    # Weak categories for this class
    weak_categories = (
        LearnerError.objects
        .filter(
            student_id__in=student_ids,
            learning_item__module__course=course,
            resolved=False,
        )
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total", "category")[:8]
    )

    # Domain stats (Aerospace domains)
    domain_map = {}
    progress_qs = LearningProgress.objects.filter(
        student_id__in=student_ids,
        learning_item__module__course=course,
    ).select_related('learning_item__aerospace_domain')

    for progress in progress_qs:
        item = progress.learning_item
        if item.aerospace_domain:
            name = item.aerospace_domain.name
        else:
            name = item.module.title if item.module else "Other"
        data = domain_map.setdefault(
            name,
            {"name": name, "correct": 0, "incorrect": 0}
        )
        data["correct"] += progress.correct_count
        data["incorrect"] += progress.incorrect_count

    domain_stats = []
    for data in domain_map.values():
        attempts = data["correct"] + data["incorrect"]
        data["accuracy"] = round(data["correct"] / attempts * 100, 1) if attempts else 0
        domain_stats.append(data)

    domain_stats.sort(key=lambda x: (x["accuracy"], x["name"]))

    return render(
        request,
        "learning/teacher_class_detail.html",
        {
            "course": course,
            "class_name": class_name or "Unassigned",
            "students": students,
            "student_count": len(students),
            "class_accuracy": class_accuracy,
            "class_mastery": class_mastery,
            "weak_categories": weak_categories,
            "domain_stats": domain_stats,
        },
    )


@login_required
def teacher_student_detail(request, student_id):
    """
    Detailed view for a specific student, visible to teachers.
    """
    _require_learning_teacher(request.user)

    student = get_object_or_404(get_user_model(), pk=student_id)

    # Get courses that this student is enrolled in and that the teacher teaches
    teacher_courses = LearningCourse.objects.filter(
        created_by=request.user,
        is_active=True,
    )
    teacher_course_ids = list(teacher_courses.values_list('id', flat=True))

    enrollments = Enrollment.objects.filter(
        student=student,
        course_id__in=teacher_course_ids,
        status=Enrollment.Status.ACTIVE,
    ).select_related('course')

    if not enrollments:
        # Student not in any of this teacher's courses
        return render(
            request,
            "learning/teacher_student_detail.html",
            {
                "student_object": student,
                "course_rows": [],
                "latest_placement": None,
                "errors": [],
                "weak_areas": [],
            }
        )

    course_ids = [enrollment.course_id for enrollment in enrollments]

    course_rows = []
    for enrollment in enrollments:
        summary = _student_course_summary(student, enrollment.course)
        course_rows.append({
            "enrollment": enrollment,
            "course": enrollment.course,
            "summary": summary,
        })

    # Latest placement attempt
    latest_placement = PlacementAttempt.objects.filter(
        student=student,
        status=PlacementAttempt.Status.COMPLETED,
    ).order_by("-completed_at").first()

    # Recent errors
    errors = LearnerError.objects.filter(
        student=student,
        learning_item__module__course_id__in=course_ids,
    ).select_related(
        "learning_item",
        "question",
    ).order_by("-occurred_at")[:20]

    # Weak areas
    weak_areas = (
        LearnerError.objects
        .filter(
            student=student,
            learning_item__module__course_id__in=course_ids,
            resolved=False,
        )
        .values("category")
        .annotate(total=Count("id"))
        .order_by("-total")[:10]
    )

    return render(
        request,
        "learning/teacher_student_detail.html",
        {
            "student_object": student,
            "course_rows": course_rows,
            "latest_placement": latest_placement,
            "errors": errors,
            "weak_areas": weak_areas,
        },
    )


# =========================================================
# Teacher Resource Creation
# =========================================================

@approved_teacher_required
def teacher_resource_create(request):

    if request.method == "POST":

        form = ResourceForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            resource = form.save(
                commit=False
            )

            resource.uploaded_by = request.user

            resource.save()

            return redirect(
                "learning:teacher_learning_dashboard"
            )

    else:

        form = ResourceForm()

    return render(
        request,
        "learning/teacher_resource_form.html",
        {
            "form": form,
        },
    )


# =========================================================
# Resource List
# =========================================================

@login_required
def resource_list(request):
    resources = Resource.objects.filter(is_public=True).order_by("-created_at")
    return render(
        request,
        "learning/resource_list.html",
        {"resources": resources},
    )