from django.contrib import admin

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