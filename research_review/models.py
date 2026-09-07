from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError


class ResearchExperiment(models.Model):
    """
    One controlled AeroESP research experiment/source:
    R003, R004, R005, R006, R007, ...
    """

    experiment_id = models.CharField(
        max_length=50,
        unique=True,
    )
    source_id = models.CharField(
        max_length=20,
        unique=True,
    )

    domain = models.CharField(max_length=150)
    topic = models.CharField(max_length=255)

    protocol = models.CharField(max_length=50)

    target_cefr = models.CharField(
        max_length=10,
        default="B2",
    )
    target_cognitive_level = models.CharField(
        max_length=30,
        default="UNDERSTAND",
    )

    source_material = models.TextField(
        blank=True,
    )

    is_confirmatory = models.BooleanField(
        default=True,
    )

    is_frozen = models.BooleanField(
        default=True,
        help_text="Frozen research experiments should not be silently modified.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["source_id"]

    def __str__(self):
        return f"{self.source_id} — {self.domain} — {self.topic}"


class ResearchRun(models.Model):
    """
    One AI generation condition within an experiment.
    Example:
    R003 + ChatGPT Free Simple / Think OFF
    """

    experiment = models.ForeignKey(
        ResearchExperiment,
        on_delete=models.PROTECT,
        related_name="runs",
    )

    run_id = models.CharField(
        max_length=80,
        unique=True,
    )

    provider = models.CharField(
        max_length=100,
    )

    displayed_model = models.CharField(
        max_length=150,
        blank=True,
    )

    condition = models.CharField(
        max_length=255,
        blank=True,
    )

    raw_output_format = models.CharField(
        max_length=100,
        default="JSON",
    )

    json_valid = models.BooleanField(
        default=True,
    )

    schema_compliant = models.BooleanField(
        default=True,
    )

    item_count_compliant = models.BooleanField(
        default=True,
    )

    skill_sequence_compliant = models.BooleanField(
        default=True,
    )

    answer_position_compliant = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            "experiment__source_id",
            "run_id",
        ]

    def __str__(self):
        return f"{self.run_id} — {self.provider}"


class ResearchQuestion(models.Model):
    """
    Research-only item.

    IMPORTANT:
    This table is intentionally separate from the operational
    assessment question bank.
    """

    SKILL_CHOICES = [
        ("main_idea", "Main Idea"),
        ("specific_information", "Specific Information"),
        ("inference", "Inference"),
        ("vocabulary_in_context", "Vocabulary in Context"),
        ("technical_comprehension", "Technical Comprehension"),
        ("cause_and_effect", "Cause and Effect"),
        ("applied_understanding", "Applied Understanding"),
    ]

    ANSWER_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
    ]

    run = models.ForeignKey(
        ResearchRun,
        on_delete=models.PROTECT,
        related_name="questions",
    )

    blind_id = models.CharField(
        max_length=30,
        unique=True,
    )

    item_number = models.PositiveSmallIntegerField()

    skill = models.CharField(
        max_length=40,
        choices=SKILL_CHOICES,
    )

    stem = models.TextField()

    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()

    correct_answer = models.CharField(
        max_length=1,
        choices=ANSWER_CHOICES,
    )

    explanation = models.TextField(
        blank=True,
    )

    source_evidence = models.TextField(
        blank=True,
    )

    raw_preserved = models.BooleanField(
        default=True,
    )

    is_validated = models.BooleanField(
        default=False,
    )

    promoted_to_operational_bank = models.BooleanField(
        default=False,
    )

    PROVENANCE_CHOICES = [
        ("AI_GENERATED", "AI Generated"),
        ("HUMAN_WRITTEN", "Human Written"),
        ("EXISTING_SOURCE", "Existing Source"),
    ]

    # Research metadata only - never rendered to a reviewer. The whole
    # point of blinded review is that this stays invisible: showing it
    # would let a reviewer's judgment be coloured by "this is
    # AI-generated" before they have actually evaluated the item.
    # review_item.html builds its context from `question` and
    # `experiment` alone (see reviewer_dashboard()/review_item() in
    # views.py) and neither template nor view ever names this field;
    # ReviewFieldBlindingTests.test_provenance_never_appears_on_the_
    # review_page in tests.py asserts this against the rendered HTML.
    question_provenance = models.CharField(
        max_length=20,
        choices=PROVENANCE_CHOICES,
        default="AI_GENERATED",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = [
            "run__experiment__source_id",
            "run__run_id",
            "item_number",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=["run", "item_number"],
                name="unique_research_item_per_run",
            )
        ]

    def __str__(self):
        return f"{self.blind_id} — {self.skill}"


class ExpertReviewerProfile(models.Model):
    """
    Additional reviewer information.
    Authentication still uses accounts.CustomUser.
    """

    DISCIPLINE_CHOICES = [
        ("AEROSPACE", "Aerospace Engineering"),
        ("ESP", "ESP / Language Assessment"),
        ("BOTH", "Aerospace + ESP"),
        ("OTHER", "Other"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expert_reviewer_profile",
    )

    discipline = models.CharField(
        max_length=20,
        choices=DISCIPLINE_CHOICES,
    )

    institution = models.CharField(
        max_length=255,
        blank=True,
    )

    is_active_reviewer = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.discipline}"


class ReviewAssignment(models.Model):
    """
    Connects one expert with one blinded research question.
    """

    STATUS_CHOICES = [
        ("NOT_STARTED", "Not Started"),
        ("IN_PROGRESS", "In Progress"),
        ("COMPLETED", "Completed"),
        ("LOCKED", "Locked"),
    ]

    reviewer = models.ForeignKey(
        ExpertReviewerProfile,
        on_delete=models.PROTECT,
        related_name="assignments",
    )

    question = models.ForeignKey(
        ResearchQuestion,
        on_delete=models.PROTECT,
        related_name="assignments",
    )

    display_order = models.PositiveIntegerField(
        default=0,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="NOT_STARTED",
    )

    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "question"],
                name="unique_reviewer_question_assignment",
            )
        ]

        ordering = [
            "reviewer",
            "display_order",
        ]

    def __str__(self):
        return f"{self.reviewer} → {self.question.blind_id}"


class ExpertReview(models.Model):
    """
    Human EVAL_V1 rating.

    Draft reviews may be incomplete so that autosave works.
    Finalized reviews must contain all mandatory EVAL_V1 fields.
    """

    DECISION_CHOICES = [
        ("ACCEPT", "Accept"),
        ("MINOR_EDIT", "Minor Edit"),
        ("MAJOR_EDIT", "Major Edit"),
        ("REJECT", "Reject"),
    ]

    YES_NO_CHOICES = [
        ("YES", "Yes"),
        ("NO", "No"),
    ]

    CEFR_CHOICES = [
        ("A2", "A2"),
        ("B1", "B1"),
        ("B2", "B2"),
        ("C1", "C1"),
        ("C2", "C2"),
    ]

    COGNITIVE_CHOICES = [
        ("REMEMBER", "Remember"),
        ("UNDERSTAND", "Understand"),
        ("APPLY", "Apply"),
        ("ANALYZE", "Analyze"),
    ]

    assignment = models.OneToOneField(
        ReviewAssignment,
        on_delete=models.PROTECT,
        related_name="review",
    )

    # =====================================================
    # Content validity (Polit & Beck, 2006)
    # Rendered above the EVAL_V1 quality dimensions - see
    # research_review/templates/research_review/review_item.html.
    #
    # A 4-point relevance scale, deliberately separate from the 5-point
    # EVAL_V1 dimensions below: this is the field a CVI computation
    # (I-CVI / S-CVI/Ave) is actually run on, since none of the
    # EVAL_V1 dimensions measure "relevance to the construct" as such.
    #
    # null=True/blank=True here, like every EVAL_V1 field, so draft
    # autosave still works with it unanswered; ExpertReview.clean()
    # is what makes it mandatory before a review can be finalized.
    # =====================================================

    construct_relevance = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(4),
        ],
        help_text=(
            "How relevant is this item to the construct of English "
            "language proficiency in the aerospace engineering "
            "domain? "
            "1=Not relevant, 2=Somewhat relevant (major revision), "
            "3=Relevant (minor revision), 4=Highly relevant"
        ),
    )

    # =====================================================
    # EVAL_V1 scores
    # Draft reviews may leave these blank.
    # =====================================================

    technical_correctness = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    linguistic_accuracy = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    clarity_answerability = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    source_fidelity = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    distractor_quality = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    cefr_alignment = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    difficulty_alignment = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    pedagogical_value = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
    )

    # =====================================================
    # Expert classifications
    # =====================================================

    expert_cefr = models.CharField(
        max_length=10,
        choices=CEFR_CHOICES,
        blank=True,
        default="",
    )

    expert_cognitive_level = models.CharField(
        max_length=20,
        choices=COGNITIVE_CHOICES,
        blank=True,
        default="",
    )

    keyed_answer_correct = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        blank=True,
        default="",
    )

    ambiguous = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        blank=True,
        default="",
    )

    multiple_correct_answers = models.CharField(
        max_length=3,
        choices=YES_NO_CHOICES,
        blank=True,
        default="",
    )

    overall_decision = models.CharField(
        max_length=20,
        choices=DECISION_CHOICES,
        blank=True,
        default="",
    )

    error_codes = models.CharField(
        max_length=255,
        blank=True,
    )

    comments = models.TextField(
        blank=True,
    )

    # =====================================================
    # Review process metadata (not part of EVAL_V1 itself)
    # =====================================================

    reviewer_confidence = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        help_text=(
            "Optional: how confident are you in this assessment? "
            "1=Not confident, 5=Very confident."
        ),
    )

    # Populated from a hidden form field the page fills in with
    # JavaScript (load timestamp -> elapsed seconds at submit); see
    # review_item() and review_item.html. Never asked of the reviewer
    # directly, so it is not a ModelForm field.
    time_spent_seconds = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    is_finalized = models.BooleanField(
        default=False,
    )

    finalized_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def clean(self):
        """
        Draft reviews may be incomplete.

        Once finalized, all mandatory EVAL_V1 fields
        must be completed.
        """

        super().clean()

        if not self.is_finalized:
            return

        required_fields = [
            "construct_relevance",
            "technical_correctness",
            "linguistic_accuracy",
            "clarity_answerability",
            "source_fidelity",
            "distractor_quality",
            "cefr_alignment",
            "difficulty_alignment",
            "pedagogical_value",
            "expert_cefr",
            "expert_cognitive_level",
            "keyed_answer_correct",
            "ambiguous",
            "multiple_correct_answers",
            "overall_decision",
        ]

        errors = {}

        for field_name in required_fields:
            value = getattr(
                self,
                field_name,
            )

            if value is None or value == "":
                errors[field_name] = (
                    "This field is required before final submission."
                )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.assignment.reviewer.user.username} - "
            f"{self.assignment.question.blind_id}"
        )


class ReviewAuditLog(models.Model):
    """
    Immutable-style audit trail for review events.
    """

    review = models.ForeignKey(
        ExpertReview,
        on_delete=models.PROTECT,
        related_name="audit_logs",
    )

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="research_review_audit_actions",
    )

    action = models.CharField(
        max_length=100,
    )

    details = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.review_id} — {self.action}"