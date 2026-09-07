from django import forms
from django.contrib import admin
from django.db.models import Q
from django.utils import timezone

from unfold.admin import ModelAdmin

from accounts.models import (
    CustomUser,
    TeacherProfile,
)

from .models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


# =========================================================
# Topic Review Form
# =========================================================

class AerospaceTopicAdminForm(forms.ModelForm):

    class Meta:
        model = AerospaceTopic
        fields = "__all__"

    def clean(self):

        cleaned_data = super().clean()

        status = cleaned_data.get(
            "approval_status"
        )

        note = cleaned_data.get(
            "review_note",
            "",
        )

        if (
            status
            == AerospaceTopic.ApprovalStatus.REJECTED
            and not note.strip()
        ):

            self.add_error(
                "review_note",
                "Enter a rejection reason before "
                "rejecting this topic proposal.",
            )

        return cleaned_data


# =========================================================
# Aerospace Domains
# =========================================================

@admin.register(AerospaceDomain)
class AerospaceDomainAdmin(ModelAdmin):

    list_display = (
        "code",
        "name",
        "order",
        "is_active",
    )

    list_editable = (
        "order",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "description",
    )

    ordering = (
        "order",
        "name",
    )

    list_per_page = 50


# =========================================================
# Aerospace Topics
# =========================================================

@admin.register(AerospaceTopic)
class AerospaceTopicAdmin(ModelAdmin):

    form = AerospaceTopicAdminForm

    list_display = (
        "code",
        "name",
        "domain",
        "parent",
        "approval_status",
        "created_by",
        "reviewed_by",
        "reviewed_at",
        "is_active",
    )

    list_filter = (
        "domain",
        "approval_status",
        "is_active",
        "reviewed_by",
    )

    search_fields = (
        "code",
        "name",
        "description",
        "domain__name",
        "parent__name",
        "created_by__username",
        "reviewed_by__username",
        "review_note",
    )

    autocomplete_fields = (
        "parent",
    )

    readonly_fields = (
        "created_by",
        "reviewed_by",
        "reviewed_at",
    )

    fieldsets = (
        (
            "Topic",
            {
                "fields": (
                    "domain",
                    "parent",
                    "code",
                    "name",
                    "description",
                    "order",
                )
            },
        ),
        (
            "Proposal",
            {
                "fields": (
                    "created_by",
                    "approval_status",
                    "is_active",
                )
            },
        ),
        (
            "Review",
            {
                "fields": (
                    "review_note",
                    "reviewed_by",
                    "reviewed_at",
                )
            },
        ),
    )

    ordering = (
        "domain__order",
        "order",
        "name",
    )

    list_per_page = 50

    actions = (
        "approve_topics",
    )

    @admin.action(
        description="Approve selected topic proposals"
    )
    def approve_topics(
        self,
        request,
        queryset,
    ):

        updated = (
            queryset
            .exclude(
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .CORE
                )
            )
            .update(
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .APPROVED
                ),
                is_active=True,
                reviewed_by=request.user,
                reviewed_at=timezone.now(),
                review_note="",
            )
        )

        self.message_user(
            request,
            f"{updated} topic proposal(s) approved.",
        )

    def save_model(
        self,
        request,
        obj,
        form,
        change,
    ):

        status = obj.approval_status

        if (
            status
            == AerospaceTopic
            .ApprovalStatus
            .APPROVED
        ):

            obj.is_active = True

            obj.reviewed_by = (
                request.user
            )

            obj.reviewed_at = (
                timezone.now()
            )

        elif (
            status
            == AerospaceTopic
            .ApprovalStatus
            .REJECTED
        ):

            obj.is_active = False

            obj.reviewed_by = (
                request.user
            )

            obj.reviewed_at = (
                timezone.now()
            )

        elif (
            status
            == AerospaceTopic
            .ApprovalStatus
            .PENDING
        ):

            obj.is_active = False

        elif (
            status
            == AerospaceTopic
            .ApprovalStatus
            .CORE
        ):

            obj.is_active = True

        super().save_model(
            request,
            obj,
            form,
            change,
        )


# =========================================================
# Questions
# =========================================================

@admin.register(Question)
class QuestionAdmin(ModelAdmin):

    list_display = (
        "id",
        "short_question",
        "domain_ref",
        "topic_ref",
        "skill",
        "difficulty",
        "status",
        "visibility",
        "source_type",
        "owner",
        "version",
    )

    list_filter = (
        "domain_ref",
        "skill",
        "difficulty",
        "question_language",
        "status",
        "visibility",
        "source_type",
    )

    search_fields = (
        "question_text",
        "explanation",
        "topic",
        "topic_ref__name",
        "topic_ref__code",
        "domain_ref__name",
        "domain_ref__code",
        "source_reference",
        "owner__username",
        "owner__first_name",
        "owner__last_name",
    )

    autocomplete_fields = (
        "topic_ref",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    list_per_page = 50

    fieldsets = (
        (
            "Question",
            {
                "fields": (
                    "owner",
                    "question_type",
                    "question_text",
                    "option_a",
                    "option_b",
                    "option_c",
                    "option_d",
                    "correct_answer",
                    "explanation",
                )
            },
        ),

        (
            "Classification",
            {
                "fields": (
                    "question_language",
                    "options_language",
                    "skill",
                    "domain_ref",
                    "topic_ref",
                    "aerospace_domain",
                    "topic",
                    "difficulty",
                )
            },
        ),

        (
            "Research provenance",
            {
                "fields": (
                    "source_type",
                    "source_reference",
                )
            },
        ),

        (
            "Publication",
            {
                "fields": (
                    "status",
                    "visibility",
                    "version",
                )
            },
        ),

        (
            "Audit",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(
        description="Question"
    )
    def short_question(
        self,
        obj,
    ):

        return obj.question_text[:70]

    def formfield_for_foreignkey(
        self,
        db_field,
        request,
        **kwargs,
    ):

        if db_field.name == "owner":

            kwargs["queryset"] = (
                CustomUser.objects.filter(
                    Q(is_superuser=True)
                    | Q(
                        teacher_profile__approval_status=(
                            TeacherProfile
                            .ApprovalStatus
                            .APPROVED
                        )
                    )
                )
                .distinct()
                .order_by(
                    "username"
                )
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )