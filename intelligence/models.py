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