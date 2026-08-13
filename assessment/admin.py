from django.contrib import admin
from django.db.models import Q

from accounts.models import CustomUser, TeacherProfile
from .models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


@admin.register(AerospaceDomain)
class AerospaceDomainAdmin(admin.ModelAdmin):

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


@admin.register(AerospaceTopic)
class AerospaceTopicAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "name",
        "domain",
        "order",
        "is_active",
    )

    list_filter = (
        "domain",
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
        "domain__name",
    )

    ordering = (
        "domain__order",
        "order",
        "name",
    )


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

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
        "topic_ref",
        "skill",
        "difficulty",
        "question_language",
        "status",
        "visibility",
        "source_type",
    )

    search_fields = (
        "question_text",
        "topic",
        "topic_ref__name",
        "domain_ref__name",
        "source_reference",
        "owner__username",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

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

    @admin.display(description="Question")
    def short_question(self, obj):
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
                        teacher_profile__approval_status=
                        TeacherProfile.ApprovalStatus.APPROVED
                    )
                )
                .distinct()
                .order_by("username")
            )

        return super().formfield_for_foreignkey(
            db_field,
            request,
            **kwargs,
        )