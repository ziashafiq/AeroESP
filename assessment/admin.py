from django.contrib import admin
from .models import Question


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        "short_question",
        "skill",
        "aerospace_domain",
        "difficulty",
        "correct_answer",
    )

    list_filter = (
        "skill",
        "aerospace_domain",
        "difficulty",
    )

    search_fields = (
        "question_text",
    )

    def short_question(self, obj):
        return obj.question_text[:60]

    short_question.short_description = "Question"