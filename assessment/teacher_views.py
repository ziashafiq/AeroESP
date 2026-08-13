from django.contrib.auth.decorators import permission_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from accounts.decorators import approved_teacher_required

from .forms import TeacherQuestionForm
from .models import Question


@approved_teacher_required
@permission_required(
    "assessment.view_question",
    raise_exception=True,
)
def teacher_question_list(request):

    questions = (
        Question.objects
        .filter(owner=request.user)
        .select_related(
            "domain_ref",
            "topic_ref",
        )
        .order_by("-updated_at")
    )

    return render(
        request,
        "assessment/teacher/question_list.html",
        {
            "questions": questions,
        },
    )


@approved_teacher_required
@permission_required(
    "assessment.add_question",
    raise_exception=True,
)
def teacher_question_create(request):

    if request.method == "POST":

        form = TeacherQuestionForm(request.POST)

        if form.is_valid():

            question = form.save(commit=False)

            # Ownership is ALWAYS assigned server-side.
            question.owner = request.user

            question.source_type = (
                Question.SourceType.MANUAL
            )

            question.status = (
                Question.Status.DRAFT
            )

            question.version = 1

            # -----------------------------------------
            # Temporary compatibility with old quiz
            # -----------------------------------------

            question.aerospace_domain = (
                question.domain_ref.code
            )

            if question.topic_ref:
                question.topic = question.topic_ref.name
            else:
                question.topic = ""

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


@approved_teacher_required
@permission_required(
    "assessment.change_question",
    raise_exception=True,
)
def teacher_question_edit(request, pk):

    # CRITICAL ownership protection:
    # A teacher can retrieve only their own question.
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

            # Never trust owner from browser input.
            updated_question.owner = request.user

            updated_question.aerospace_domain = (
                updated_question.domain_ref.code
            )

            if updated_question.topic_ref:
                updated_question.topic = (
                    updated_question.topic_ref.name
                )
            else:
                updated_question.topic = ""

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