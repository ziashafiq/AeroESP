from django.conf import settings
from django.db import models


class QuestionAISuggestion(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    question = models.ForeignKey(
        "assessment.Question",
        on_delete=models.CASCADE,
        related_name="ai_suggestions",
    )

    suggested_track = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    suggested_skill = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    suggested_difficulty = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    suggested_domain = models.ForeignKey(
        "assessment.AerospaceDomain",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_question_suggestions",
    )

    suggested_topic = models.ForeignKey(
        "assessment.AerospaceTopic",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_question_suggestions",
    )

    confidence = models.DecimalField(
        max_digits=4,
        decimal_places=3,
        default=0,
    )

    rationale = models.TextField(
        blank=True,
        default="",
    )

    backend = models.CharField(
        max_length=80,
        default="RULE_BASED_V1",
    )

    raw_output = models.JSONField(
        default=dict,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_ai_question_suggestions",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_ai_question_suggestions",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

        indexes = [
            models.Index(
                fields=[
                    "question",
                    "status",
                ],
                name="ai_question_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"AI suggestion for "
            f"question {self.question_id}"
        )


class LearnerInsightSnapshot(models.Model):

    class Scope(models.TextChoices):
        GENERAL = "GENERAL", "General English"
        AEROSPACE = "AEROSPACE", "Aerospace English"
        OVERALL = "OVERALL", "Overall"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_insight_snapshots",
    )

    scope = models.CharField(
        max_length=20,
        choices=Scope.choices,
        default=Scope.OVERALL,
    )

    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    risk_band = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    summary = models.TextField(
        blank=True,
        default="",
    )

    recommendations = models.JSONField(
        default=list,
        blank=True,
    )

    evidence = models.JSONField(
        default=dict,
        blank=True,
    )

    backend = models.CharField(
        max_length=80,
        default="EXPLAINABLE_BASELINE_V1",
    )

    generated_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ["-generated_at"]

        indexes = [
            models.Index(
                fields=[
                    "student",
                    "generated_at",
                ],
                name="ai_insight_student_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.scope} - "
            f"{self.risk_band}"
        )


class GeneratedQuestionDraft(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending Review"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_generated_question_drafts",
    )

    track = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    skill = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    difficulty = models.CharField(
        max_length=40,
        blank=True,
        default="",
    )

    domain = models.ForeignKey(
        "assessment.AerospaceDomain",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_generated_drafts",
    )

    topic = models.ForeignKey(
        "assessment.AerospaceTopic",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_generated_drafts",
    )

    theme = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )

    teacher_instructions = models.TextField(
        blank=True,
        default="",
    )

    question_text = models.TextField()

    option_a = models.CharField(
        max_length=500,
    )

    option_b = models.CharField(
        max_length=500,
    )

    option_c = models.CharField(
        max_length=500,
    )

    option_d = models.CharField(
        max_length=500,
    )

    correct_answer = models.CharField(
        max_length=1,
    )

    explanation = models.TextField(
        blank=True,
        default="",
    )

    provider = models.CharField(
        max_length=80,
        default="BASELINE_V1",
    )

    generation_metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_question = models.ForeignKey(
        "assessment.Question",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="originating_ai_drafts",
    )

    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_ai_generated_drafts",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "created_by",
                    "status",
                ],
                name="ai_draft_owner_status_idx",
            ),
        ]

    def __str__(self):
        return (
            f"AI Draft {self.pk} - "
            f"{self.status}"
        )


# =========================================================
# AI / Research Telemetry
# =========================================================

class AIInteractionEvent(models.Model):

    class EventType(models.TextChoices):

        GENERATION_SUCCESS = (
            "GENERATION_SUCCESS",
            "Question Generation Success",
        )

        GENERATION_FAILURE = (
            "GENERATION_FAILURE",
            "Question Generation Failure",
        )

        DRAFT_EDITED = (
            "DRAFT_EDITED",
            "Generated Draft Edited",
        )

        DRAFT_ACCEPTED = (
            "DRAFT_ACCEPTED",
            "Generated Draft Accepted",
        )

        DRAFT_REJECTED = (
            "DRAFT_REJECTED",
            "Generated Draft Rejected",
        )

        QUESTION_ANALYSIS = (
            "QUESTION_ANALYSIS",
            "Question Analysis",
        )

        LEARNER_INSIGHT = (
            "LEARNER_INSIGHT",
            "Learner Insight",
        )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_interaction_events",
    )

    subject_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_subject_events",
    )

    draft = models.ForeignKey(
        "GeneratedQuestionDraft",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="interaction_events",
    )

    question = models.ForeignKey(
        "assessment.Question",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="ai_interaction_events",
    )

    event_type = models.CharField(
        max_length=40,
        choices=EventType.choices,
    )

    provider = models.CharField(
        max_length=80,
        blank=True,
        default="",
    )

    model_name = models.CharField(
        max_length=120,
        blank=True,
        default="",
    )

    prompt_version = models.CharField(
        max_length=80,
        blank=True,
        default="",
    )

    success = models.BooleanField(
        default=True,
    )

    latency_ms = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    input_tokens = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    output_tokens = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    total_tokens = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    request_id = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "event_type",
                    "created_at",
                ],
                name="ai_event_type_time_idx",
            ),
            models.Index(
                fields=[
                    "actor",
                    "created_at",
                ],
                name="ai_event_actor_time_idx",
            ),
        ]

    def __str__(self):

        return (
            f"{self.event_type} - "
            f"{self.created_at}"
        )
