from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class LearningProgram(models.Model):

    class ProgramType(models.TextChoices):
        IELTS = "IELTS", "IELTS / General English"
        AEROSPACE_ESP = (
            "AEROSPACE_ESP",
            "Aerospace English / ESP",
        )

    code = models.SlugField(
        max_length=60,
        unique=True,
    )

    title = models.CharField(
        max_length=150,
    )

    title_fa = models.CharField(
        max_length=150,
        blank=True,
    )

    program_type = models.CharField(
        max_length=30,
        choices=ProgramType.choices,
    )

    description = models.TextField(
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    order = models.PositiveIntegerField(
        default=1,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "order",
            "title",
        ]

    def __str__(self):
        return self.title


class LearningCourse(models.Model):

    class Level(models.TextChoices):
        BEGINNER = "BEGINNER", "Beginner"
        ELEMENTARY = "ELEMENTARY", "Elementary"
        PRE_INTERMEDIATE = (
            "PRE_INTERMEDIATE",
            "Pre-Intermediate",
        )
        INTERMEDIATE = (
            "INTERMEDIATE",
            "Intermediate",
        )
        UPPER_INTERMEDIATE = (
            "UPPER_INTERMEDIATE",
            "Upper-Intermediate",
        )
        ADVANCED = "ADVANCED", "Advanced"
        IELTS_5 = "IELTS_5", "IELTS Band 5"
        IELTS_55 = "IELTS_55", "IELTS Band 5.5"
        IELTS_6 = "IELTS_6", "IELTS Band 6"
        IELTS_65 = "IELTS_65", "IELTS Band 6.5"
        IELTS_7_PLUS = (
            "IELTS_7_PLUS",
            "IELTS Band 7+",
        )
        ESP_FOUNDATION = (
            "ESP_FOUNDATION",
            "ESP Foundation",
        )
        ESP_ADVANCED = (
            "ESP_ADVANCED",
            "Advanced ESP",
        )

    program = models.ForeignKey(
        LearningProgram,
        on_delete=models.PROTECT,
        related_name="courses",
    )

    code = models.SlugField(
        max_length=80,
        unique=True,
    )

    title = models.CharField(
        max_length=200,
    )

    title_fa = models.CharField(
        max_length=200,
        blank=True,
    )

    description = models.TextField(
        blank=True,
    )

    level = models.CharField(
        max_length=30,
        choices=Level.choices,
        blank=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    is_public = models.BooleanField(
        default=True,
    )

    order = models.PositiveIntegerField(
        default=1,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_learning_courses",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "program",
            "order",
            "title",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "program",
                    "title",
                ],
                name=(
                    "uq_learning_course_"
                    "program_title"
                ),
            ),
        ]

    def __str__(self):
        return self.title


class CourseModule(models.Model):

    class ModuleType(models.TextChoices):
        VOCABULARY = (
            "VOCABULARY",
            "Vocabulary",
        )
        GRAMMAR = (
            "GRAMMAR",
            "Grammar",
        )
        READING = (
            "READING",
            "Reading",
        )
        LISTENING = (
            "LISTENING",
            "Listening",
        )
        WRITING = (
            "WRITING",
            "Writing",
        )
        SPEAKING = (
            "SPEAKING",
            "Speaking",
        )
        PRONUNCIATION = (
            "PRONUNCIATION",
            "Pronunciation",
        )
        IELTS_SKILL = (
            "IELTS_SKILL",
            "IELTS Skill",
        )
        ESP_TOPIC = (
            "ESP_TOPIC",
            "Aerospace ESP Topic",
        )
        REVIEW = (
            "REVIEW",
            "Review",
        )
        EXAM = (
            "EXAM",
            "Exam",
        )

    course = models.ForeignKey(
        LearningCourse,
        on_delete=models.CASCADE,
        related_name="modules",
    )

    aerospace_domain = models.ForeignKey(
        "assessment.AerospaceDomain",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="learning_modules",
    )

    title = models.CharField(
        max_length=200,
    )

    title_fa = models.CharField(
        max_length=200,
        blank=True,
    )

    module_type = models.CharField(
        max_length=30,
        choices=ModuleType.choices,
    )

    description = models.TextField(
        blank=True,
    )

    order = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "course",
            "order",
            "title",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "course",
                    "order",
                ],
                name=(
                    "uq_course_module_order"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.course.title} - "
            f"{self.title}"
        )


class LearningItem(models.Model):

    class ItemType(models.TextChoices):
        WORD = "WORD", "Word"
        PHRASE = "PHRASE", "Phrase"
        COLLOCATION = (
            "COLLOCATION",
            "Collocation",
        )
        PHRASAL_VERB = (
            "PHRASAL_VERB",
            "Phrasal Verb",
        )
        GRAMMAR_RULE = (
            "GRAMMAR_RULE",
            "Grammar Rule",
        )
        COMMON_ERROR = (
            "COMMON_ERROR",
            "Common Error",
        )
        READING_NOTE = (
            "READING_NOTE",
            "Reading Note",
        )
        LISTENING_NOTE = (
            "LISTENING_NOTE",
            "Listening Note",
        )
        WRITING_PATTERN = (
            "WRITING_PATTERN",
            "Writing Pattern",
        )
        SPEAKING_PATTERN = (
            "SPEAKING_PATTERN",
            "Speaking Pattern",
        )
        TECHNICAL_TERM = (
            "TECHNICAL_TERM",
            "Technical Term",
        )
        OTHER = "OTHER", "Other"

    class SourceType(models.TextChoices):
        PERSONAL = (
            "PERSONAL",
            "Personal Study",
        )
        TEACHER = (
            "TEACHER",
            "Teacher",
        )
        BOOK = "BOOK", "Book"
        COURSE = "COURSE", "Course"
        ARTICLE = "ARTICLE", "Article"
        WEBSITE = "WEBSITE", "Website"
        AI_ASSISTED = (
            "AI_ASSISTED",
            "AI Assisted",
        )
        OTHER = "OTHER", "Other"

    module = models.ForeignKey(
        CourseModule,
        on_delete=models.CASCADE,
        related_name="items",
    )

    aerospace_domain = models.ForeignKey(
        "assessment.AerospaceDomain",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="learning_items",
    )

    aerospace_topic = models.ForeignKey(
        "assessment.AerospaceTopic",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="learning_items",
    )

    english_focus = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    english_topic = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="learning_items",
    )

    title = models.CharField(
        max_length=250,
    )

    item_type = models.CharField(
        max_length=30,
        choices=ItemType.choices,
    )

    meaning_fa = models.TextField(
        blank=True,
    )

    definition_en = models.TextField(
        blank=True,
    )

    explanation = models.TextField(
        blank=True,
    )

    example = models.TextField(
        blank=True,
    )

    common_mistake = models.TextField(
        blank=True,
    )

    correct_form = models.TextField(
        blank=True,
    )

    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        default=SourceType.PERSONAL,
    )

    source_reference = models.CharField(
        max_length=500,
        blank=True,
    )

    tags = models.JSONField(
        default=list,
        blank=True,
    )

    is_verified = models.BooleanField(
        default=False,
    )

    is_public = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "module",
                    "item_type",
                ],
                name=(
                    "learning_item_type_idx"
                ),
            ),
            models.Index(
                fields=[
                    "created_by",
                    "created_at",
                ],
                name=(
                    "learning_item_user_idx"
                ),
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.aerospace_topic
            and not self.aerospace_domain
        ):
            raise ValidationError(
                {
                    "aerospace_domain":
                        "Select an aerospace domain "
                        "before selecting a topic."
                }
            )

        if (
            self.aerospace_topic
            and self.aerospace_domain
            and self.aerospace_topic.domain_id
            != self.aerospace_domain_id
        ):
            raise ValidationError(
                {
                    "aerospace_topic":
                        "The selected topic does not belong "
                        "to the selected aerospace domain."
                }
            )

    def __str__(self):
        return self.title


class LearningItemQuestion(models.Model):

    learning_item = models.ForeignKey(
        LearningItem,
        on_delete=models.CASCADE,
        related_name="question_links",
    )

    question = models.ForeignKey(
        "assessment.Question",
        on_delete=models.CASCADE,
        related_name="learning_item_links",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "learning_item",
                    "question",
                ],
                name=(
                    "uq_learning_item_question"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.learning_item} -> "
            f"Question {self.question_id}"
        )


class Enrollment(models.Model):

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = (
            "COMPLETED",
            "Completed",
        )
        PAUSED = "PAUSED", "Paused"

    class PlacementStatus(models.TextChoices):
        NOT_ASSESSED = (
            "NOT_ASSESSED",
            "Not Assessed",
        )
        PLACEMENT_TEST = (
            "PLACEMENT_TEST",
            "Placement Test",
        )
        TEACHER_ASSIGNED = (
            "TEACHER_ASSIGNED",
            "Teacher Assigned",
        )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_enrollments",
    )

    course = models.ForeignKey(
        LearningCourse,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    assigned_level = models.CharField(
        max_length=30,
        choices=LearningCourse.Level.choices,
        blank=True,
    )

    class_name = models.CharField(
        max_length=100,
        blank=True,
    )

    placement_status = models.CharField(
        max_length=30,
        choices=PlacementStatus.choices,
        default=PlacementStatus.NOT_ASSESSED,
    )

    placement_updated_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    enrolled_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "course",
                ],
                name=(
                    "uq_learning_enrollment"
                ),
            ),
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.course}"
        )


class LearningProgress(models.Model):

    class Status(models.TextChoices):
        NEW = "NEW", "New"
        LEARNING = "LEARNING", "Learning"
        REVIEW = "REVIEW", "Review"
        MASTERED = "MASTERED", "Mastered"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learning_progress",
    )

    learning_item = models.ForeignKey(
        LearningItem,
        on_delete=models.CASCADE,
        related_name="progress_records",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW,
    )

    correct_count = models.PositiveIntegerField(
        default=0,
    )

    incorrect_count = models.PositiveIntegerField(
        default=0,
    )

    review_count = models.PositiveIntegerField(
        default=0,
    )

    mastery_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    last_reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    next_review_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "learning_item",
                ],
                name=(
                    "uq_learning_progress"
                ),
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "student",
                    "next_review_at",
                ],
                name=(
                    "learning_review_due_idx"
                ),
            ),
        ]

    def schedule_next_review(
        self,
    ):

        intervals = [
            1,
            3,
            7,
            14,
            30,
            60,
        ]

        index = min(
            self.review_count,
            len(intervals) - 1,
        )

        self.next_review_at = (
            timezone.now()
            + timedelta(
                days=intervals[index]
            )
        )


class LearnerError(models.Model):

    class ErrorCategory(models.TextChoices):
        VOCABULARY = (
            "VOCABULARY",
            "Vocabulary",
        )
        COLLOCATION = (
            "COLLOCATION",
            "Collocation",
        )
        GRAMMAR = (
            "GRAMMAR",
            "Grammar",
        )
        PREPOSITION = (
            "PREPOSITION",
            "Preposition",
        )
        ARTICLE = (
            "ARTICLE",
            "Article",
        )
        WORD_FORM = (
            "WORD_FORM",
            "Word Formation",
        )
        SPELLING = (
            "SPELLING",
            "Spelling",
        )
        READING = (
            "READING",
            "Reading",
        )
        LISTENING = (
            "LISTENING",
            "Listening",
        )
        WRITING = (
            "WRITING",
            "Writing",
        )
        SPEAKING = (
            "SPEAKING",
            "Speaking",
        )
        TECHNICAL_TERM = (
            "TECHNICAL_TERM",
            "Technical Terminology",
        )
        TECHNICAL_READING = (
            "TECHNICAL_READING",
            "Technical Reading",
        )
        OTHER = "OTHER", "Other"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="learner_errors",
    )

    question = models.ForeignKey(
        "assessment.Question",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learner_errors",
    )

    learning_item = models.ForeignKey(
        LearningItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="learner_errors",
    )

    category = models.CharField(
        max_length=30,
        choices=ErrorCategory.choices,
    )

    student_response = models.TextField(
        blank=True,
    )

    expected_response = models.TextField(
        blank=True,
    )

    note = models.TextField(
        blank=True,
    )

    is_general_english_error = (
        models.BooleanField(
            default=False,
        )
    )

    is_esp_specific_error = (
        models.BooleanField(
            default=False,
        )
    )

    resolved = models.BooleanField(
        default=False,
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
    )

    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-occurred_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "student",
                    "category",
                ],
                name=(
                    "learner_error_cat_idx"
                ),
            ),
            models.Index(
                fields=[
                    "is_general_english_error",
                    "is_esp_specific_error",
                ],
                name=(
                    "learner_error_scope_idx"
                ),
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.is_general_english_error
            and self.is_esp_specific_error
        ):
            raise ValidationError(
                "An error cannot be both "
                "general-English-only and "
                "ESP-specific."
            )

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.get_category_display()}"
        )


class PlacementAttempt(models.Model):
    """
    Records a student's attempt at a placement test.
    """

    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="placement_attempts",
    )

    program = models.ForeignKey(
        LearningProgram,
        on_delete=models.CASCADE,
        related_name="placement_attempts",
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    vocabulary_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    grammar_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    reading_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    listening_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    overall_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
    )

    cefr_level = models.CharField(
        max_length=10,
        blank=True,
        default="",
    )

    ielts_estimate = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-started_at",
        ]

        indexes = [
            models.Index(
                fields=[
                    "student",
                    "program",
                    "status",
                ],
                name="placement_student_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.program} - "
            f"{self.status}"
        )


class PlacementQuestion(models.Model):
    """
    Links a question to a placement test pool for a specific program.
    """

    program = models.ForeignKey(
        LearningProgram,
        on_delete=models.CASCADE,
        related_name="placement_questions",
    )

    question = models.ForeignKey(
        "assessment.Question",
        on_delete=models.PROTECT,
        related_name="placement_questions",
    )

    order = models.PositiveIntegerField(
        default=0,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "order",
            "id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "program",
                    "question",
                ],
                name="uq_placement_question",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "program",
                    "is_active",
                    "order",
                ],
                name="placement_pool_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.program} -> "
            f"Question {self.question_id}"
        )


class PlacementResponse(models.Model):
    """
    Records a student's answer to a placement question.
    """

    attempt = models.ForeignKey(
        PlacementAttempt,
        on_delete=models.CASCADE,
        related_name="responses",
    )

    question = models.ForeignKey(
        "assessment.Question",
        on_delete=models.PROTECT,
        related_name="placement_responses",
    )

    selected_answer = models.CharField(
        max_length=1,
    )

    correct_answer_snapshot = models.CharField(
        max_length=1,
    )

    skill_snapshot = models.CharField(
        max_length=30,
        blank=True,
        default="",
    )

    is_correct = models.BooleanField(
        default=False,
    )

    answered_at = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "attempt",
                    "question",
                ],
                name="uq_placement_response",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "attempt",
                    "skill_snapshot",
                ],
                name="placement_resp_idx",
            ),
        ]

    def __str__(self):
        return (
            f"Attempt {self.attempt_id} - "
            f"Question {self.question_id}"
        )