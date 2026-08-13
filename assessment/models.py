from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


# =========================================================
# Aerospace Taxonomy
# =========================================================

class AerospaceDomain(models.Model):
    """
    Top-level aerospace taxonomy domain.

    Examples:
    - Aerodynamics & Fluid Mechanics
    - Flight Mechanics, Dynamics & Control
    - Propulsion & Power Systems
    - Space Engineering & Astronautics
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
        ordering = (
            "order",
            "name",
        )

    def __str__(self):
        return self.name


class AerospaceTopic(models.Model):
    """
    Flexible hierarchical aerospace topic.

    A topic belongs to one AerospaceDomain and may
    optionally have another topic as its parent.

    Example:

    Flight Dynamics & Control
        └── Guidance
            └── Missile Guidance
    """

    class ApprovalStatus(models.TextChoices):
        CORE = "CORE", "Core AeroESP Topic"
        PENDING = "PENDING", "Pending Review"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    domain = models.ForeignKey(
        AerospaceDomain,
        on_delete=models.CASCADE,
        related_name="topics",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="children",
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

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_aerospace_topics",
    )

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.CORE,
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
                fields=(
                    "domain",
                    "code",
                ),
                name="unique_topic_code_per_domain",
            )
        ]

    def clean(self):
        super().clean()

        # Parent topic must belong to the same domain.
        if self.parent:
            if self.parent.domain_id != self.domain_id:
                raise ValidationError(
                    {
                        "parent":
                            "Parent topic must belong to "
                            "the same aerospace domain."
                    }
                )

        # A topic cannot be its own parent.
        if self.pk and self.parent_id == self.pk:
            raise ValidationError(
                {
                    "parent":
                        "A topic cannot be its own parent."
                }
            )

    def __str__(self):
        if self.parent:
            return (
                f"{self.domain.name} → "
                f"{self.parent.name} → "
                f"{self.name}"
            )

        return f"{self.domain.name} → {self.name}"


# =========================================================
# Question Bank
# =========================================================

class Question(models.Model):

    # -----------------------------------------------------
    # Language Skill
    # -----------------------------------------------------

    class Skill(models.TextChoices):
        VOCABULARY = (
            "VOCAB",
            "Technical Vocabulary",
        )

        GRAMMAR = (
            "GRAMMAR",
            "Grammar in Engineering Context",
        )

        READING = (
            "READING",
            "Technical Reading",
        )

    # -----------------------------------------------------
    # Legacy Domain Codes
    #
    # Temporary compatibility layer for the old quiz.
    # We now include all major AeroESP domains so new
    # questions can safely use the expanded taxonomy.
    # -----------------------------------------------------

    class Domain(models.TextChoices):
        GENERAL = (
            "GENERAL",
            "General Aerospace & Fundamentals",
        )

        AERODYNAMICS = (
            "AERO",
            "Aerodynamics & Fluid Mechanics",
        )

        FLIGHT_DYNAMICS = (
            "FLIGHT",
            "Flight Mechanics, Dynamics & Control",
        )

        PROPULSION = (
            "PROP",
            "Propulsion & Power Systems",
        )

        STRUCTURES = (
            "STRUCT",
            "Structures & Materials",
        )

        DESIGN = (
            "DESIGN",
            "Aircraft Design & Performance",
        )

        AVIONICS = (
            "AVIONICS",
            "Avionics, Navigation & Sensors",
        )

        SPACE = (
            "SPACE",
            "Space Engineering & Astronautics",
        )

        UAV = (
            "UAV",
            "UAV, Robotics & Autonomous Systems",
        )

        SYSTEMS = (
            "SYSTEMS",
            "Systems Engineering, Safety & Reliability",
        )

        MAINTENANCE = (
            "MAINT",
            "Manufacturing, Maintenance & Airworthiness",
        )

        METHODS = (
            "METHODS",
            "Experimental, Computational & Data Methods",
        )

    # -----------------------------------------------------
    # Difficulty
    # -----------------------------------------------------

    class Difficulty(models.TextChoices):
        BASIC = (
            "BASIC",
            "Basic",
        )

        INTERMEDIATE = (
            "INTERMEDIATE",
            "Intermediate",
        )

        ADVANCED = (
            "ADVANCED",
            "Advanced",
        )

    # -----------------------------------------------------
    # Question Type
    # -----------------------------------------------------

    class QuestionType(models.TextChoices):
        SINGLE_MCQ = (
            "SINGLE_MCQ",
            "Single-answer MCQ",
        )

    # -----------------------------------------------------
    # Language
    # -----------------------------------------------------

    class Language(models.TextChoices):
        ENGLISH = (
            "EN",
            "English",
        )

        PERSIAN = (
            "FA",
            "Persian",
        )

    # -----------------------------------------------------
    # Provenance
    # -----------------------------------------------------

    class SourceType(models.TextChoices):
        MANUAL = (
            "MANUAL",
            "Teacher / Human Authored",
        )

        SEED = (
            "SEED",
            "Demo Seed Data",
        )

        CORPUS = (
            "CORPUS",
            "Corpus-derived",
        )

        IMPORTED = (
            "IMPORTED",
            "Imported",
        )

        AI = (
            "AI",
            "AI Generated",
        )

    # -----------------------------------------------------
    # Review Status
    # -----------------------------------------------------

    class Status(models.TextChoices):
        DRAFT = (
            "DRAFT",
            "Draft",
        )

        REVIEW = (
            "REVIEW",
            "Under Review",
        )

        APPROVED = (
            "APPROVED",
            "Approved",
        )

        DEMO = (
            "DEMO",
            "Demo",
        )

        RETIRED = (
            "RETIRED",
            "Retired",
        )

    # -----------------------------------------------------
    # Visibility
    # -----------------------------------------------------

    class Visibility(models.TextChoices):
        PRIVATE = (
            "PRIVATE",
            "Teacher Private",
        )

        PRACTICE_EXAM = (
            "PRACTICE_EXAM",
            "Practice + Exam",
        )

        EXAM_ONLY = (
            "EXAM_ONLY",
            "Exam Only",
        )

        SHARED = (
            "SHARED",
            "Shared Teacher Bank",
        )

        AEROESP_BANK = (
            "AEROESP_BANK",
            "AeroESP Bank",
        )

    # =====================================================
    # Ownership
    # =====================================================

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="authored_questions",
    )

    # =====================================================
    # Question Content
    # =====================================================

    question_type = models.CharField(
        max_length=30,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE_MCQ,
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

    # =====================================================
    # Language
    # =====================================================

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

    # =====================================================
    # Educational Classification
    # =====================================================

    skill = models.CharField(
        max_length=20,
        choices=Skill.choices,
    )

    # -----------------------------------------------------
    # Legacy fields
    #
    # Temporarily retained for compatibility.
    # They will be removed after Quiz Engine v2 fully
    # replaces the original quiz.
    # -----------------------------------------------------

    aerospace_domain = models.CharField(
        max_length=20,
        choices=Domain.choices,
    )

    topic = models.CharField(
        max_length=200,
        blank=True,
    )

    # -----------------------------------------------------
    # Research-ready taxonomy
    # -----------------------------------------------------

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

    difficulty = models.CharField(
        max_length=20,
        choices=Difficulty.choices,
        default=Difficulty.BASIC,
    )

    # =====================================================
    # Research Provenance
    # =====================================================

    source_type = models.CharField(
        max_length=20,
        choices=SourceType.choices,
        default=SourceType.MANUAL,
    )

    source_reference = models.CharField(
        max_length=500,
        blank=True,
    )

    # =====================================================
    # Review / Publication State
    # =====================================================

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

    # =====================================================
    # Audit
    # =====================================================

    created_at = models.DateTimeField(
        default=timezone.now,
        editable=False,
    )

    updated_at = models.DateTimeField(
        default=timezone.now,
    )

    # =====================================================
    # Validation
    # =====================================================

    def clean(self):
        super().clean()

        # A Topic cannot be selected without a Domain.
        if self.topic_ref and not self.domain_ref:
            raise ValidationError(
                {
                    "domain_ref":
                        "Select an aerospace domain "
                        "before selecting a topic."
                }
            )

        # Topic must belong to selected Domain.
        if self.topic_ref and self.domain_ref:
            if self.topic_ref.domain_id != self.domain_ref_id:
                raise ValidationError(
                    {
                        "topic_ref":
                            "Selected topic does not belong "
                            "to the selected aerospace domain."
                    }
                )

    # =====================================================
    # Save
    # =====================================================

    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()

        # Keep legacy fields synchronized automatically
        # while the old quiz still exists.
        if self.domain_ref:
            self.aerospace_domain = self.domain_ref.code

        if self.topic_ref:
            self.topic = self.topic_ref.name

        super().save(*args, **kwargs)

    # =====================================================
    # Display
    # =====================================================

    def __str__(self):
        return self.question_text[:80]