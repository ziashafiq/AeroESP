from django.contrib import admin, messages
from django.db import transaction

from .models import (
    ExpertReviewerProfile,
    ExpertReview,
    ResearchExperiment,
    ResearchQuestion,
    ResearchRun,
    ReviewAssignment,
    ReviewAuditLog,
)


# =========================================================
# Frozen Research Experiments
# =========================================================

@admin.register(ResearchExperiment)
class ResearchExperimentAdmin(admin.ModelAdmin):

    list_display = (
        "source_id",
        "experiment_id",
        "domain",
        "topic",
        "protocol",
        "target_cefr",
        "target_cognitive_level",
        "is_frozen",
    )

    list_filter = (
        "domain",
        "protocol",
        "target_cefr",
        "target_cognitive_level",
        "is_frozen",
    )

    search_fields = (
        "source_id",
        "experiment_id",
        "domain",
        "topic",
    )

    ordering = (
        "source_id",
    )

    readonly_fields = tuple(
        field.name
        for field in ResearchExperiment._meta.fields
    )

    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Frozen AI Runs
# =========================================================

@admin.register(ResearchRun)
class ResearchRunAdmin(admin.ModelAdmin):

    list_display = (
        "run_id",
        "experiment",
        "provider",
        "displayed_model",
        "json_valid",
        "schema_compliant",
        "item_count_compliant",
        "skill_sequence_compliant",
        "answer_position_compliant",
    )

    list_filter = (
        "experiment",
        "provider",
        "json_valid",
        "schema_compliant",
        "item_count_compliant",
        "skill_sequence_compliant",
        "answer_position_compliant",
    )

    search_fields = (
        "run_id",
        "provider",
        "displayed_model",
        "condition",
        "experiment__source_id",
    )

    ordering = (
        "experiment__source_id",
        "run_id",
    )

    readonly_fields = tuple(
        field.name
        for field in ResearchRun._meta.fields
    )

    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Frozen Research Questions
# =========================================================

@admin.register(ResearchQuestion)
class ResearchQuestionAdmin(admin.ModelAdmin):

    list_display = (
        "blind_id",
        "source_id",
        "provider",
        "item_number",
        "skill",
        "correct_answer",
        "question_provenance",
        "is_validated",
        "promoted_to_operational_bank",
    )

    list_filter = (
        "run__experiment",
        "run__provider",
        "skill",
        "correct_answer",
        "question_provenance",
        "is_validated",
        "promoted_to_operational_bank",
    )

    search_fields = (
        "blind_id",
        "stem",
        "run__run_id",
        "run__provider",
        "run__experiment__source_id",
    )

    ordering = (
        "blind_id",
    )

    readonly_fields = tuple(
        field.name
        for field in ResearchQuestion._meta.fields
    )

    list_per_page = 100

    @admin.display(
        description="Source",
        ordering="run__experiment__source_id",
    )
    def source_id(self, obj):
        return obj.run.experiment.source_id

    @admin.display(
        description="Provider",
        ordering="run__provider",
    )
    def provider(self, obj):
        return obj.run.provider

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "run",
                "run__experiment",
            )
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Expert Reviewer Profiles
# =========================================================

@admin.register(ExpertReviewerProfile)
class ExpertReviewerProfileAdmin(admin.ModelAdmin):

    list_display = (
        "reviewer_code",
        "user",
        "discipline",
        "institution",
        "is_active_reviewer",
        "assignment_count",
        "created_at",
    )

    list_filter = (
        "discipline",
        "is_active_reviewer",
        "institution",
    )

    search_fields = (
        "reviewer_code",
        "user__username",
        "user__first_name",
        "user__last_name",
        "user__email",
        "institution",
    )

    autocomplete_fields = (
        "user",
    )

    list_editable = (
        "is_active_reviewer",
    )

    readonly_fields = (
        "created_at",
    )

    list_per_page = 50

    @admin.display(description="Assignments")
    def assignment_count(self, obj):
        return obj.assignments.count()

    def has_delete_permission(self, request, obj=None):
        # Reviewers should normally be deactivated,
        # not deleted.
        return False


# =========================================================
# Review Assignments
# =========================================================

@admin.register(ReviewAssignment)
class ReviewAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "reviewer_name",
        "blind_id",
        "display_order",
        "status",
        "assigned_at",
    )

    list_filter = (
        "status",
        "reviewer",
        "question__run__experiment",
    )

    search_fields = (
        "reviewer__user__username",
        "reviewer__user__first_name",
        "reviewer__user__last_name",
        "question__blind_id",
    )

    autocomplete_fields = (
        "reviewer",
        "question",
    )

    ordering = (
        "reviewer",
        "display_order",
    )

    list_per_page = 100

    @admin.display(
        description="Reviewer",
        ordering="reviewer__user__username",
    )
    def reviewer_name(self, obj):
        name = obj.reviewer.user.get_full_name()
        return name or obj.reviewer.user.username

    @admin.display(
        description="Blind ID",
        ordering="question__blind_id",
    )
    def blind_id(self, obj):
        return obj.question.blind_id

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "reviewer",
                "reviewer__user",
                "question",
                "question__run",
                "question__run__experiment",
            )
        )

    def get_readonly_fields(
        self,
        request,
        obj=None,
    ):
        if obj:
            return (
                "reviewer",
                "question",
                "status",
                "assigned_at",
            )

        return (
            "status",
            "assigned_at",
        )

    def has_delete_permission(self, request, obj=None):
        return False


# =========================================================
# Expert Reviews
# =========================================================

@admin.register(ExpertReview)
class ExpertReviewAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "reviewer_name",
        "blind_id",
        "overall_decision",
        "is_finalized",
        "updated_at",
        "finalized_at",
    )

    list_filter = (
        "is_finalized",
        "overall_decision",
        "expert_cefr",
        "expert_cognitive_level",
        "keyed_answer_correct",
        "ambiguous",
        "multiple_correct_answers",
    )

    search_fields = (
        "assignment__reviewer__user__username",
        "assignment__reviewer__user__first_name",
        "assignment__reviewer__user__last_name",
        "assignment__question__blind_id",
        "comments",
        "error_codes",
    )

    ordering = (
        "-updated_at",
    )

    readonly_fields = tuple(
        field.name
        for field in ExpertReview._meta.fields
    )

    list_per_page = 100

    actions = (
        "unlock_selected_reviews",
    )

    @admin.display(
        description="Reviewer",
        ordering="assignment__reviewer__user__username",
    )
    def reviewer_name(self, obj):
        user = obj.assignment.reviewer.user
        return user.get_full_name() or user.username

    @admin.display(
        description="Blind ID",
        ordering="assignment__question__blind_id",
    )
    def blind_id(self, obj):
        return obj.assignment.question.blind_id

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "assignment",
                "assignment__reviewer",
                "assignment__reviewer__user",
                "assignment__question",
            )
        )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(
        description=(
            "Unlock selected finalized reviews "
            "(audited)"
        )
    )
    def unlock_selected_reviews(
        self,
        request,
        queryset,
    ):

        unlocked = 0

        with transaction.atomic():

            reviews = (
                queryset
                .select_for_update()
                .select_related(
                    "assignment",
                    "assignment__question",
                )
            )

            for review in reviews:

                assignment = review.assignment

                if (
                    not review.is_finalized
                    and assignment.status != "LOCKED"
                ):
                    continue

                previous_status = assignment.status

                review.is_finalized = False
                review.finalized_at = None
                review.save()

                assignment.status = "IN_PROGRESS"
                assignment.save(
                    update_fields=["status"]
                )

                ReviewAuditLog.objects.create(
                    review=review,
                    actor=request.user,
                    action="ADMIN_UNLOCK",
                    details={
                        "assignment_id": assignment.id,
                        "blind_id": (
                            assignment.question.blind_id
                        ),
                        "previous_status": previous_status,
                        "new_status": "IN_PROGRESS",
                    },
                )

                unlocked += 1

        if unlocked:
            self.message_user(
                request,
                (
                    f"{unlocked} review(s) unlocked "
                    "and audit logged."
                ),
                level=messages.SUCCESS,
            )
        else:
            self.message_user(
                request,
                "No finalized or locked reviews were selected.",
                level=messages.WARNING,
            )


# =========================================================
# Immutable Review Audit Log
# =========================================================

@admin.register(ReviewAuditLog)
class ReviewAuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "review",
        "blind_id",
        "action",
        "actor",
        "created_at",
    )

    list_filter = (
        "action",
        "actor",
        "created_at",
    )

    search_fields = (
        "review__assignment__question__blind_id",
        "review__assignment__reviewer__user__username",
        "actor__username",
        "action",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = tuple(
        field.name
        for field in ReviewAuditLog._meta.fields
    )

    list_per_page = 100

    @admin.display(
        description="Blind ID",
        ordering="review__assignment__question__blind_id",
    )
    def blind_id(self, obj):
        return obj.review.assignment.question.blind_id

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related(
                "review",
                "review__assignment",
                "review__assignment__question",
                "review__assignment__reviewer",
                "review__assignment__reviewer__user",
                "actor",
            )
        )

    def has_add_permission(self, request):
        return False

    def has_change_permission(
        self,
        request,
        obj=None,
    ):
        # Audit records are view-only.
        return False

    def has_delete_permission(
        self,
        request,
        obj=None,
    ):
        return False