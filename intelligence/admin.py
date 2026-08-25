from django.contrib import admin

from .models import (
    AIInteractionEvent,
    GeneratedQuestionDraft,
    LearnerInsightSnapshot,
    QuestionAISuggestion,
)


@admin.register(
    QuestionAISuggestion
)
class QuestionAISuggestionAdmin(
    admin.ModelAdmin
):

    list_display = (
        "question",
        "suggested_track",
        "suggested_skill",
        "confidence",
        "status",
        "backend",
        "created_at",
    )

    list_filter = (
        "status",
        "backend",
        "suggested_track",
        "suggested_skill",
    )

    search_fields = (
        "question__question_text",
        "rationale",
    )


@admin.register(
    LearnerInsightSnapshot
)
class LearnerInsightSnapshotAdmin(
    admin.ModelAdmin
):

    list_display = (
        "student",
        "scope",
        "risk_band",
        "risk_score",
        "backend",
        "generated_at",
    )

    list_filter = (
        "scope",
        "risk_band",
        "backend",
    )

    search_fields = (
        "student__username",
        "summary",
    )


@admin.register(
    GeneratedQuestionDraft
)
class GeneratedQuestionDraftAdmin(
    admin.ModelAdmin
):

    list_display = (
        "id",
        "created_by",
        "track",
        "skill",
        "difficulty",
        "provider",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "provider",
        "track",
        "skill",
        "difficulty",
    )

    search_fields = (
        "question_text",
        "theme",
        "created_by__username",
    )


@admin.register(
    AIInteractionEvent
)
class AIInteractionEventAdmin(
    admin.ModelAdmin
):

    list_display = (
        "event_type",
        "actor",
        "provider",
        "model_name",
        "success",
        "latency_ms",
        "total_tokens",
        "created_at",
    )

    list_filter = (
        "event_type",
        "success",
        "provider",
        "model_name",
    )

    search_fields = (
        "actor__username",
        "request_id",
        "provider",
        "model_name",
    )

    readonly_fields = (
        "created_at",
    )
