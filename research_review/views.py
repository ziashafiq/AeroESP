from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import (
    staff_member_required,
)
from django.db.models import Avg, Count
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.utils import timezone

from accounts.models import HelpGuide

from .decorators import expert_reviewer_required
from .forms import ExpertReviewForm
from .models import (
    ExpertReview,
    ReviewAssignment,
    ReviewAuditLog,
)


GETTING_STARTED_SLUG = "expert-reviewer-getting-started"


def getting_started(request):
    """
    A stable, shareable link for inviting professors to review AI-
    generated questions.

    Public and requires no account, since the whole point is to walk
    someone through registering. If the admin has written a guide for
    this under Help Guides (slug 'expert-reviewer-getting-started'),
    it is used instead of the built-in explanation below - so wording
    can be corrected without a code change once real guidance exists.
    """

    guide = HelpGuide.objects.filter(
        slug=GETTING_STARTED_SLUG,
        is_published=True,
    ).first()

    if guide:
        return redirect(guide.get_absolute_url())

    return render(
        request,
        "research_review/getting_started.html",
        {
            "support_email": settings.AEROESP_SUPPORT_EMAIL,
        },
    )


@expert_reviewer_required
def reviewer_dashboard(request):

    reviewer = request.expert_reviewer

    assignments = (
        ReviewAssignment.objects
        .filter(
            reviewer=reviewer
        )
        .select_related(
            "question",
            "question__run",
            "question__run__experiment",
        )
        .order_by(
            "display_order",
            "id",
        )
    )

    total = assignments.count()

    not_started = assignments.filter(
        status="NOT_STARTED"
    ).count()

    in_progress = assignments.filter(
        status="IN_PROGRESS"
    ).count()

    locked = assignments.filter(
        status="LOCKED"
    ).count()

    progress_percent = (
        round(
            (locked / total) * 100
        )
        if total
        else 0
    )

    next_assignment = (
        assignments
        .exclude(
            status="LOCKED"
        )
        .first()
    )

    return render(
        request,
        "research_review/dashboard.html",
        {
            "reviewer": reviewer,
            "assignments": assignments,
            "total": total,
            "not_started": not_started,
            "in_progress": in_progress,
            "locked": locked,
            "progress_percent": progress_percent,
            "next_assignment": next_assignment,
        },
    )


@expert_reviewer_required
def review_item(
    request,
    assignment_id,
):

    reviewer = request.expert_reviewer

    assignment = get_object_or_404(
        ReviewAssignment.objects
        .select_related(
            "question",
            "question__run",
            "question__run__experiment",
        ),
        pk=assignment_id,
        reviewer=reviewer,
    )

    review, _ = (
        ExpertReview.objects
        .get_or_create(
            assignment=assignment
        )
    )

    locked = (
        review.is_finalized
        or assignment.status == "LOCKED"
    )

    if request.method == "POST":

        if locked:

            messages.error(
                request,
                "This review has already been finalized and locked.",
            )

            return redirect(
                "research_review:review_item",
                assignment_id=assignment.pk,
            )

        form = ExpertReviewForm(
            request.POST,
            instance=review,
        )

        if form.is_valid():

            action = request.POST.get(
                "action",
                "draft",
            )

            review_object = form.save(
                commit=False
            )

            # Not a ModelForm field - filled in by JavaScript from
            # page-load to submit (see review_item.html) rather than
            # asked of the reviewer, so it is read from POST directly.
            # An absent, blank, or tampered-with value degrades to
            # "not recorded" rather than a 500.
            submitted_time_spent = request.POST.get(
                "time_spent_seconds",
                "",
            ).strip()

            if submitted_time_spent.isdigit():
                review_object.time_spent_seconds = int(
                    submitted_time_spent
                )

            if action == "finalize":

                review_object.is_finalized = True
                review_object.finalized_at = (
                    timezone.now()
                )

                try:
                    review_object.full_clean()

                except ValidationError as exc:

                    if hasattr(
                        exc,
                        "message_dict",
                    ):

                        for (
                            field_name,
                            error_messages,
                        ) in exc.message_dict.items():

                            target_field = (
                                field_name
                                if field_name
                                in form.fields
                                else None
                            )

                            for error_message in error_messages:

                                form.add_error(
                                    target_field,
                                    error_message,
                                )

                    else:

                        form.add_error(
                            None,
                            exc,
                        )

                else:

                    with transaction.atomic():

                        review_object.save()

                        assignment.status = (
                            "LOCKED"
                        )

                        assignment.save(
                            update_fields=[
                                "status",
                            ]
                        )

                        ReviewAuditLog.objects.create(
                            review=review_object,
                            actor=request.user,
                            action="FINAL_SUBMIT",
                            details={
                                "assignment_id":
                                    assignment.pk,

                                "blind_id":
                                    assignment.question.blind_id,

                                "status":
                                    "LOCKED",
                            },
                        )

                    messages.success(
                        request,
                        "Review finalized and locked successfully.",
                    )

                    return redirect(
                        "research_review:dashboard"
                    )

            else:

                with transaction.atomic():

                    review_object.is_finalized = False
                    review_object.finalized_at = None

                    review_object.save()

                    if (
                        assignment.status
                        == "NOT_STARTED"
                    ):

                        assignment.status = (
                            "IN_PROGRESS"
                        )

                        assignment.save(
                            update_fields=[
                                "status",
                            ]
                        )

                messages.success(
                    request,
                    "Draft saved.",
                )

                return redirect(
                    "research_review:review_item",
                    assignment_id=assignment.pk,
                )

    else:

        form = ExpertReviewForm(
            instance=review
        )

    if locked:

        for field in form.fields.values():
            field.disabled = True

    question = assignment.question
    experiment = question.run.experiment

    return render(
        request,
        "research_review/review_item.html",
        {
            "assignment": assignment,
            "question": question,
            "experiment": experiment,
            "review": review,
            "form": form,
            "locked": locked,
        },
    )

# =========================================================
# Study analysis
#
# Researcher-facing, and staff-only on purpose. Reviewers must not see
# how the panel as a whole is scoring while they are still scoring:
# aggregate means and a decision split are exactly the kind of anchor
# that would pull later judgements toward the group.
#
# Nothing here touches provenance. The charts are built from
# ExpertReview alone and never join to ResearchRun or
# ResearchExperiment, so there is no path from this page to which
# service or condition produced a question. See
# research_review/tests.py for the assertions that hold that.
# =========================================================

DIMENSIONS = [
    ("construct_relevance", "Construct relevance"),
    ("technical_correctness", "Technical correctness"),
    ("linguistic_accuracy", "Linguistic accuracy"),
    ("clarity_answerability", "Clarity / answerability"),
    ("source_fidelity", "Source fidelity"),
    ("distractor_quality", "Distractor quality"),
    ("cefr_alignment", "CEFR alignment"),
    ("difficulty_alignment", "Difficulty alignment"),
    ("pedagogical_value", "Pedagogical value"),
]


@staff_member_required
def analysis(request):

    finalized = ExpertReview.objects.filter(is_finalized=True)

    total = finalized.count()

    # One aggregate query for all nine means rather than nine queries.
    averages = finalized.aggregate(
        **{
            name: Avg(name)
            for name, _label in DIMENSIONS
        }
    )

    dimension_series = [
        {
            "label": label,
            "mean": (
                round(float(averages[name]), 2)
                if averages[name] is not None
                else None
            ),
        }
        for name, label in DIMENSIONS
    ]

    counts = dict(
        finalized
        .exclude(overall_decision="")
        .values_list("overall_decision")
        .annotate(n=Count("id"))
    )

    # Built from the model's own choices so a decision nobody picked
    # still shows as a zero rather than vanishing from the chart.
    decision_series = [
        {
            "label": label,
            "value": counts.get(value, 0),
        }
        for value, label in ExpertReview.DECISION_CHOICES
    ]

    reviewers_reporting = (
        finalized
        .values("assignment__reviewer")
        .distinct()
        .count()
    )

    confidence = finalized.aggregate(
        mean=Avg("reviewer_confidence")
    )["mean"]

    return render(
        request,
        "research_review/analysis.html",
        {
            "total": total,
            "reviewers_reporting": reviewers_reporting,
            "dimension_series": dimension_series,
            "decision_series": decision_series,
            "mean_confidence": (
                round(float(confidence), 2)
                if confidence is not None
                else None
            ),
        },
    )
