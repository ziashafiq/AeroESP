from django.contrib import admin
from django.db.models import Q

from accounts.models import CustomUser, TeacherProfile
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "short_question",
        "skill",
        "aerospace_domain",
        "difficulty",
        "status",
        "visibility",
        "source_type",
        "owner",
        "version",
    )

    list_filter = (
        "skill",
        "aerospace_domain",
        "difficulty",
        "question_language",
        "status",
        "visibility",
        "source_type",
    )

    search_fields = (
        "question_text",
        "topic",
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

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Limit Question.owner to:
        1. Superusers/Admins
        2. Approved teachers

        Students, pending teachers, and rejected teachers
        must not appear in the Owner selector.
        """

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