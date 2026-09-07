from django.conf import settings
from django.contrib import messages
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