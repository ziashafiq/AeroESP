from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class AerospaceDomain(models.Model):
    """
    Top-level aerospace taxonomy domain.
    Examples:
    Aerodynamics, Flight Dynamics & Control, Propulsion.
    """

    code = models.CharField(
        max_length=30,
        unique=True,
    )

    name = models.CharField(
        max_length=200,
        unique=True,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = ("order", "name")

    def __str__(self):
        return self.name


class AerospaceTopic(models.Model):
    """
    Second level of the aerospace taxonomy.
    Each topic belongs to one AerospaceDomain.
    """

    domain = models.ForeignKey(
        AerospaceDomain,
        on_delete=models.CASCADE,
        related_name="topics",
    )

    code = models.CharField(
        max_length=50,
    )

    name = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    class Meta:
        ordering = (
            "domain__order",
            "order",
            "name",
        )

        constraints = [
            models.UniqueConstraint(
                fields=("domain", "code"),
                name="unique_topic_code_per_domain",
            )
        ]

    def __str__(self):
        return f"{self.domain.name} → {self.name}"


class Question(models.Model):

    # -------------------------------------------------
    # Legacy classifications
    # Kept temporarily so the existing quiz continues
    # working while we migrate to the new taxonomy.
    # -------------------------------------------------

    class Skill(models.TextChoices):
        VOCABULARY = "VOCAB", "Technical Vocabulary"
        GRAMMAR = "GRAMMAR", "Grammar in Engineering Context"
        READING = "READING", "Technical Reading"

    class Domain(models.TextChoices):
        AERODYNAMICS = "AERO", "Aerodynamics"
        FLIGHT_DYNAMICS = "FLIGHT", "Flight Dynamics & Control"
        PROPULSION = "PROP", "Propulsion"

    class Difficulty(models.TextChoices):
        BASIC = "BASIC", "Basic"
        INTERMEDIATE = "INTERMEDIATE", "Intermediate"
        ADVANCED = "ADVANCED", "Advanced"

    # -------------------------------------------------
    # Question Architecture v2
    # -------------------------------------------------

    class QuestionType(models.TextChoices):
        SINGLE_MCQ = "SINGLE_MCQ", "Single-answer MCQ"

    class Language(models.TextChoices):
        ENGLISH = "EN", "English"
        PERSIAN = "FA", "Persian"

    class SourceType(models.TextChoices):
        MANUAL = "MANUAL", "Teacher / Human Authored"
        SEED = "SEED", "Demo Seed Data"
        CORPUS = "CORPUS", "Corpus-derived"
        IMPORTED = "IMPORTED", "Imported"
        AI = "AI", "AI Generated"

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        REVIEW = "REVIEW", "Under Review"
        APPROVED = "APPROVED", "Approved"
        DEMO = "DEMO", "Demo"
        RETIRED = "RETIRED", "Retired"

    class Visibility(models.TextChoices):
        PRIVATE = "PRIVATE", "Teacher Private"
        PRACTICE_EXAM = "PRACTICE_EXAM", "Practice + Exam"
        EXAM_ONLY = "EXAM_ONLY", "Exam Only"
        SHARED = "SHARED", "Shared Teacher Bank"
        AEROESP_BANK = "AEROESP_BANK", "AeroESP Bank"

    # -------------------------------------------------
    # Ownership
    # -------------------------------------------------

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_questions",
    )

    # -------------------------------------------------
    # Question content
    # -------------------------------------------------

    question_type = models.CharField(
        max_length=30,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_MCQ,
    )

    question_text = models.TextField()

    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)

    correct_answer = models.CharField(
        max_length=1,
        choices=[
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
        ],
    )

    explanation = models.TextField(
        blank=True,
    )

    # -------------------------------------------------
    # Language
    # -------------------------------------------------

    question_language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.ENGLISH,
    )

    options_language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.ENGLISH,
    )

    # -------------------------------------------------
    # Legacy educational classification
    # -------------------------------------------------

    skill = models.CharField(
        max_length=20,
        choices=Skill.choices,
    )

    aerospace_domain = models.CharField(
        max_length=20,
        choices=Domain.choices,
    )

    topic = models.CharField(
        max_length=200,
        blank=True,
    )

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BASIC,
    )

    # -------------------------------------------------
    # New research-ready aerospace taxonomy
    # -------------------------------------------------

    domain_ref = models.ForeignKey(
        AerospaceDomain,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="questions",
    )

    topic_ref = models.ForeignKey(
        AerospaceTopic,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="questions",
    )

    # -------------------------------------------------
    # Research provenance
    # -------------------------------------------------

    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.MANUAL,
    )

    source_reference = models.CharField(
        max_length=500,
        blank=True,
    )

    # -------------------------------------------------
    # Review / publication state
    # -------------------------------------------------

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    visibility = models.CharField(
        max_length=30,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
    )

    version = models.PositiveIntegerField(
        default=1,
    )

    # -------------------------------------------------
    # Audit timestamps
    # -------------------------------------------------

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    updated_at = models.DateTimeField(
        default=timezone.now,
    )

    def clean(self):
        super().clean()

        if self.topic_ref and self.domain_ref:
            if self.topic_ref.domain_id != self.domain_ref_id:
                raise ValidationError(
                    {
                        "topic_ref":
                            "Selected topic does not belong "
                            "to the selected aerospace domain."
                    }
                )

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.question_text[:80]