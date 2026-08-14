from django.contrib import admin

from .models import (
    Exam,
    ExamAttempt,
    ExamEvent,
    ExamQuestion,
    StudentAnswer,
)


class ExamQuestionInline(admin.TabularInline):
    model = ExamQuestion
    extra = 0
    autocomplete_fields = [
        "question",
    ]
    fields = [
        "order",
        "question",
        "points",
        "required",
        "question_version",
    ]
    ordering = [
        "order",
    ]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "title",
        "owner",
        "mode",
        "status",
        "duration_minutes",
        "starts_at",
        "ends_at",
        "created_at",
    ]

    list_filter = [
        "mode",
        "status",
        "result_policy",
        "shuffle_questions",
        "shuffle_options",
    ]

    search_fields = [
        "title",
        "description",
        "owner__username",
        "owner__email",
        "access_code",
    ]

    autocomplete_fields = [
        "owner",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
        "published_at",
    ]

    inlines = [
        ExamQuestionInline,
    ]


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "exam",
        "order",
        "question",
        "points",
        "question_version",
        "required",
    ]

    list_filter = [
        "required",
    ]

    search_fields = [
        "exam__title",
        "question__question_text",
    ]

    autocomplete_fields = [
        "exam",
        "question",
    ]

    ordering = [
        "exam",
        "order",
    ]


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "exam",
        "student",
        "attempt_number",
        "status",
        "score",
        "max_score",
        "percentage",
        "started_at",
        "submitted_at",
    ]

    list_filter = [
        "status",
        "exam",
    ]

    search_fields = [
        "exam__title",
        "student__username",
        "student__email",
    ]

    autocomplete_fields = [
        "exam",
        "student",
    ]

    readonly_fields = [
        "created_at",
        "last_activity_at",
    ]


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "attempt",
        "exam_question",
        "selected_answer",
        "is_correct",
        "awarded_points",
        "answer_change_count",
        "time_spent_ms",
    ]

    list_filter = [
        "is_correct",
        "selected_answer",
    ]

    search_fields = [
        "attempt__student__username",
        "attempt__exam__title",
    ]

    autocomplete_fields = [
        "attempt",
        "exam_question",
    ]

    readonly_fields = [
        "created_at",
        "updated_at",
    ]


@admin.register(ExamEvent)
class ExamEventAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "attempt",
        "exam_question",
        "event_type",
        "occurred_at",
    ]

    list_filter = [
        "event_type",
    ]

    search_fields = [
        "attempt__student__username",
        "attempt__exam__title",
    ]

    autocomplete_fields = [
        "attempt",
        "exam_question",
    ]

    readonly_fields = [
        "occurred_at",
    ]