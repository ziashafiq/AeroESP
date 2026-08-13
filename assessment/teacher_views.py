from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils.text import slugify

from accounts.decorators import approved_teacher_required

from .forms import (
    TeacherQuestionForm,
    TeacherTopicProposalForm,
)
from .models import (
    AerospaceTopic,
    Question,
)


# =========================================================
# Helper Functions
# =========================================================

def generate_topic_code(domain, name):
    """
    Generate a unique topic code inside one aerospace domain.

    Example:
    Fault-Tolerant Flight Control
    ->
    FAULT_TOLERANT_FLIGHT_CONTROL
    """

    base = slugify(
        name,
        allow_unicode=False,
    )

    base = (
        base
        .replace("-", "_")
        .upper()
    )

    if not base:
        base = "TOPIC"

    base = base[:40]

    code = base
    counter = 2

    while AerospaceTopic.objects.filter(
        domain=domain,
        code=code,
    ).exists():

        suffix = f"_{counter}"

        code = (
            f"{base[:50 - len(suffix)]}"
            f"{suffix}"
        )

        counter += 1

    return code


# =========================================================
# Topic Search API
# =========================================================

@approved_teacher_required
def teacher_topic_search(request):
    """
    Search approved/core aerospace topics.

    Optional query parameters:

    domain=<domain id>
    q=<search text>

    The endpoint is used by:
    - Teacher Question Form
    - Teacher Topic Proposal Form
    """

    domain_id = request.GET.get(
        "domain",
        "",
    )

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    topics = (
        AerospaceTopic.objects
        .filter(
            is_active=True,
            approval_status__in=[
                AerospaceTopic.ApprovalStatus.CORE,
                AerospaceTopic.ApprovalStatus.APPROVED,
            ],
        )
        .select_related(
            "domain",
            "parent",
        )
    )

    # -----------------------------------------------------
    # Filter by selected Aerospace Domain
    # -----------------------------------------------------

    if domain_id:

        topics = topics.filter(
            domain_id=domain_id
        )

    # -----------------------------------------------------
    # Search
    # -----------------------------------------------------

    if search_query:

        topics = topics.filter(
            Q(
                name__icontains=search_query
            )
            | Q(
                code__icontains=search_query
            )
            | Q(
                parent__name__icontains=search_query
            )
            | Q(
                domain__name__icontains=search_query
            )
            | Q(
                description__icontains=search_query
            )
        )

    topics = topics.order_by(
        "domain__order",
        "order",
        "name",
    )[:200]

    results = []

    for topic in topics:

        # Hierarchical label
        if topic.parent:

            label = (
                f"{topic.parent.name} → "
                f"{topic.name}"
            )

        else:

            label = topic.name

        results.append(
            {
                "id": topic.id,
                "code": topic.code,
                "name": topic.name,
                "label": label,
                "domain_id": topic.domain_id,
                "domain": topic.domain.name,
            }
        )

    return JsonResponse(
        {
            "results": results,
            "count": len(results),
        }
    )


# =========================================================
# Teacher Question Bank
# =========================================================

@approved_teacher_required
@permission_required(
    "assessment.view_question",
    raise_exception=True,
)
def teacher_question_list(request):
    """
    Show only questions owned by the logged-in teacher.
    """

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    questions = (
        Question.objects
        .filter(
            owner=request.user
        )
        .select_related(
            "domain_ref",
            "topic_ref",
        )
    )

    if search_query:

        questions = questions.filter(
            Q(
                question_text__icontains=search_query
            )
            | Q(
                explanation__icontains=search_query
            )
            | Q(
                domain_ref__name__icontains=search_query
            )
            | Q(
                topic_ref__name__icontains=search_query
            )
            | Q(
                source_reference__icontains=search_query
            )
        )

    questions = questions.order_by(
        "-updated_at"
    )

    return render(
        request,
        "assessment/teacher/question_list.html",
        {
            "questions": questions,
            "search_query": search_query,
        },
    )


# =========================================================
# Create Question
# =========================================================

@approved_teacher_required
@permission_required(
    "assessment.add_question",
    raise_exception=True,
)
def teacher_question_create(request):

    if request.method == "POST":

        form = TeacherQuestionForm(
            request.POST
        )

        if form.is_valid():

            question = form.save(
                commit=False
            )

            # Owner is always assigned server-side.
            question.owner = request.user

            question.source_type = (
                Question.SourceType.MANUAL
            )

            question.status = (
                Question.Status.DRAFT
            )

            question.version = 1

            question.save()

            return redirect(
                "teacher_questions:list"
            )

    else:

        form = TeacherQuestionForm()

    return render(
        request,
        "assessment/teacher/question_form.html",
        {
            "form": form,
            "page_title": "Create Question",
            "submit_label": "Create Question",
        },
    )


# =========================================================
# Edit Question
# =========================================================

@approved_teacher_required
@permission_required(
    "assessment.change_question",
    raise_exception=True,
)
def teacher_question_edit(
    request,
    pk,
):
    """
    A teacher may edit only their own questions.
    """

    question = get_object_or_404(
        Question,
        pk=pk,
        owner=request.user,
    )

    if request.method == "POST":

        form = TeacherQuestionForm(
            request.POST,
            instance=question,
        )

        if form.is_valid():

            updated_question = form.save(
                commit=False
            )

            # Never trust ownership from browser input.
            updated_question.owner = (
                request.user
            )

            if form.has_changed():

                updated_question.version += 1

            updated_question.save()

            return redirect(
                "teacher_questions:list"
            )

    else:

        form = TeacherQuestionForm(
            instance=question
        )

    return render(
        request,
        "assessment/teacher/question_form.html",
        {
            "form": form,
            "question": question,
            "page_title": "Edit Question",
            "submit_label": "Save Changes",
        },
    )


# =========================================================
# Teacher Topic Proposal List
# =========================================================

@approved_teacher_required
def teacher_topic_proposal_list(request):
    """
    Show only topic proposals submitted by the
    currently logged-in teacher.
    """

    search_query = request.GET.get(
        "q",
        "",
    ).strip()

    proposals = (
        AerospaceTopic.objects
        .filter(
            created_by=request.user
        )
        .select_related(
            "domain",
            "parent",
        )
    )

    if search_query:

        proposals = proposals.filter(
            Q(
                name__icontains=search_query
            )
            | Q(
                domain__name__icontains=search_query
            )
            | Q(
                parent__name__icontains=search_query
            )
            | Q(
                description__icontains=search_query
            )
        )

    proposals = proposals.order_by(
        "-id"
    )

    return render(
        request,
        "assessment/teacher/topic_proposal_list.html",
        {
            "proposals": proposals,
            "search_query": search_query,
        },
    )


# =========================================================
# Create Topic Proposal
# =========================================================

@approved_teacher_required
def teacher_topic_proposal_create(request):
    """
    Approved teachers may propose a new aerospace topic.

    New proposals:
    - are created as PENDING
    - are inactive
    - cannot be used in questions until Admin approval
    """

    if request.method == "POST":

        form = TeacherTopicProposalForm(
            request.POST
        )

        if form.is_valid():

            proposal = form.save(
                commit=False
            )

            # Generate internal code automatically.
            proposal.code = generate_topic_code(
                proposal.domain,
                proposal.name,
            )

            proposal.created_by = (
                request.user
            )

            proposal.approval_status = (
                AerospaceTopic
                .ApprovalStatus
                .PENDING
            )

            # Pending topics are unavailable
            # to Question Bank until approved.
            proposal.is_active = False

            # Put custom proposals after core topics.
            proposal.order = 999

            proposal.save()

            return redirect(
                "teacher_questions:topic_proposals"
            )

    else:

        form = TeacherTopicProposalForm()

    return render(
        request,
        "assessment/teacher/topic_proposal_form.html",
        {
            "form": form,
        },
    )