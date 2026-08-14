from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


TEACHERS_GROUP = "Teachers"
STUDENTS_GROUP = "Students"


def user_is_in_group(user, group_name):
    """
    Return True when a persisted user belongs to the requested Django Group.
    """
    if not user or not getattr(user, "pk", None):
        return False

    return user.groups.filter(
        name=group_name,
    ).exists()


class Exam(models.Model):

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Draft"
        PUBLISHED = "PUBLISHED", "Published"
        CLOSED = "CLOSED", "Closed"
        ARCHIVED = "ARCHIVED", "Archived"

    class Mode(models.TextChoices):
        PRACTICE = "PRACTICE", "Practice"
        SECURE = "SECURE", "Secure Exam"
        PLACEMENT = "PLACEMENT", "Placement"

    class ResultPolicy(models.TextChoices):
        IMMEDIATE = "IMMEDIATE", "Immediate"
        AFTER_CLOSE = "AFTER_CLOSE", "After Exam Closes"
        MANUAL = "MANUAL", "Teacher Release"
        HIDDEN = "HIDDEN", "Hidden"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_exams",
    )

    title = models.CharField(
        max_length=200,
    )

    description = models.TextField(
        blank=True,
    )

    instructions = models.TextField(
        blank=True,
    )

    mode = models.CharField(
        max_length=20,
        choices=Mode.choices,
        default=Mode.SECURE,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    access_code = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
    )

    duration_minutes = models.PositiveIntegerField(
        default=60,
        validators=[
            MinValueValidator(1),
        ],
    )

    starts_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    ends_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    max_attempts = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
        ],
    )

    shuffle_questions = models.BooleanField(
        default=False,
    )

    shuffle_options = models.BooleanField(
        default=False,
    )

    result_policy = models.CharField(
        max_length=20,
        choices=ResultPolicy.choices,
        default=ResultPolicy.AFTER_CLOSE,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    questions = models.ManyToManyField(
        "assessment.Question",
        through="ExamQuestion",
        related_name="used_in_exams",
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
                    "owner",
                    "status",
                ],
                name="exam_owner_status_idx",
            ),
            models.Index(
                fields=[
                    "starts_at",
                ],
                name="exam_starts_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.owner_id:
            owner_is_teacher = user_is_in_group(
                self.owner,
                TEACHERS_GROUP,
            )

            # Superusers are also accepted so that Django Admin
            # remains usable for administrative recovery/testing.
            if not owner_is_teacher and not self.owner.is_superuser:
                errors["owner"] = (
                    "Exam owner must belong to the Teachers group."
                )

        if (
            self.starts_at
            and self.ends_at
            and self.ends_at <= self.starts_at
        ):
            errors["ends_at"] = (
                "Exam end time must be later than start time."
            )

        if errors:
            raise ValidationError(errors)

    def is_available_at(self, moment=None):
        """
        Return whether the exam is currently available for starting.

        Runtime permission, student assignment, max-attempt checks,
        and access-code validation are intentionally handled later
        by the exam workflow layer.
        """
        moment = moment or timezone.now()

        if self.status != self.Status.PUBLISHED:
            return False

        if self.starts_at and moment < self.starts_at:
            return False

        if self.ends_at and moment > self.ends_at:
            return False

        return True

    def __str__(self):
        return self.title


class ExamQuestion(models.Model):

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="exam_questions",
    )

    question = models.ForeignKey(
        "assessment.Question",
        on_delete=models.PROTECT,
        related_name="exam_question_links",
    )

    order = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
        ],
    )

    points = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("1.00"),
        validators=[
            MinValueValidator(
                Decimal("0.01"),
            ),
        ],
    )

    required = models.BooleanField(
        default=True,
    )

    question_version = models.PositiveIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
        ],
    )

    # Frozen research/audit copy of the item will be stored
    # here when an exam is published.
    snapshot = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "order",
            "id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "exam",
                    "question",
                ],
                name="uq_exam_question",
            ),
            models.UniqueConstraint(
                fields=[
                    "exam",
                    "order",
                ],
                name="uq_exam_question_order",
            ),
        ]

    def __str__(self):
        return (
            f"{self.exam.title} - "
            f"Question {self.order}"
        )


class ExamAttempt(models.Model):

    class Status(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        SUBMITTED = "SUBMITTED", "Submitted"
        AUTO_SUBMITTED = "AUTO_SUBMITTED", "Auto Submitted"
        EXPIRED = "EXPIRED", "Expired"
        CANCELLED = "CANCELLED", "Cancelled"

    exam = models.ForeignKey(
        Exam,
        on_delete=models.PROTECT,
        related_name="attempts",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="exam_attempts",
    )

    attempt_number = models.PositiveSmallIntegerField(
        default=1,
        validators=[
            MinValueValidator(1),
        ],
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.IN_PROGRESS,
    )

    started_at = models.DateTimeField(
        default=timezone.now,
    )

    deadline_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
    )

    max_score = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
            MaxValueValidator(
                Decimal("100.00"),
            ),
        ],
    )

    last_activity_at = models.DateTimeField(
        auto_now=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-started_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "exam",
                    "student",
                    "attempt_number",
                ],
                name="uq_exam_student_attempt_number",
            ),

            # A student must never have two simultaneous
            # IN_PROGRESS attempts for the same exam.
            models.UniqueConstraint(
                fields=[
                    "exam",
                    "student",
                ],
                condition=models.Q(
                    status="IN_PROGRESS",
                ),
                name="uq_one_active_attempt_per_exam_student",
            ),
        ]

        indexes = [
            models.Index(
                fields=[
                    "exam",
                    "status",
                ],
                name="attempt_exam_status_idx",
            ),
            models.Index(
                fields=[
                    "student",
                    "status",
                ],
                name="attempt_student_status_idx",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if self.student_id:
            if not user_is_in_group(
                self.student,
                STUDENTS_GROUP,
            ):
                errors["student"] = (
                    "Exam attempt user must belong "
                    "to the Students group."
                )

        if self.exam_id:
            if self.attempt_number > self.exam.max_attempts:
                errors["attempt_number"] = (
                    "Attempt number exceeds the exam's "
                    "maximum allowed attempts."
                )

        if (
            self.deadline_at
            and self.deadline_at <= self.started_at
        ):
            errors["deadline_at"] = (
                "Attempt deadline must be later than start time."
            )

        if (
            self.submitted_at
            and self.submitted_at < self.started_at
        ):
            errors["submitted_at"] = (
                "Submission time cannot precede start time."
            )

        if errors:
            raise ValidationError(errors)

    @property
    def is_active(self):
        return self.status == self.Status.IN_PROGRESS

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.exam} - "
            f"Attempt {self.attempt_number}"
        )


class StudentAnswer(models.Model):

    class AnswerChoice(models.TextChoices):
        A = "A", "A"
        B = "B", "B"
        C = "C", "C"
        D = "D", "D"

    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )

    exam_question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.PROTECT,
        related_name="student_answers",
    )

    selected_answer = models.CharField(
        max_length=1,
        choices=AnswerChoice.choices,
        blank=True,
    )

    is_correct = models.BooleanField(
        null=True,
        blank=True,
    )

    awarded_points = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(
                Decimal("0.00"),
            ),
        ],
    )

    first_answered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    last_answered_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    answer_change_count = models.PositiveIntegerField(
        default=0,
    )

    time_spent_ms = models.PositiveBigIntegerField(
        default=0,
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
                    "attempt",
                    "exam_question",
                ],
                name="uq_attempt_exam_question_answer",
            ),
        ]

    def clean(self):
        super().clean()

        errors = {}

        if (
            self.attempt_id
            and self.exam_question_id
            and self.attempt.exam_id
            != self.exam_question.exam_id
        ):
            errors["exam_question"] = (
                "The answer question must belong "
                "to the attempt's exam."
            )

        if (
            self.exam_question_id
            and self.awarded_points
            > self.exam_question.points
        ):
            errors["awarded_points"] = (
                "Awarded points cannot exceed "
                "the question's maximum points."
            )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return (
            f"{self.attempt} - "
            f"Q{self.exam_question.order}"
        )


class ExamEvent(models.Model):

    class EventType(models.TextChoices):
        ATTEMPT_STARTED = (
            "ATTEMPT_STARTED",
            "Attempt Started",
        )
        QUESTION_VIEWED = (
            "QUESTION_VIEWED",
            "Question Viewed",
        )
        ANSWER_SAVED = (
            "ANSWER_SAVED",
            "Answer Saved",
        )
        ANSWER_CHANGED = (
            "ANSWER_CHANGED",
            "Answer Changed",
        )
        PAGE_FOCUS = (
            "PAGE_FOCUS",
            "Page Focus",
        )
        PAGE_BLUR = (
            "PAGE_BLUR",
            "Page Blur",
        )
        SUBMITTED = (
            "SUBMITTED",
            "Submitted",
        )
        AUTO_SUBMITTED = (
            "AUTO_SUBMITTED",
            "Auto Submitted",
        )
        RECONNECTED = (
            "RECONNECTED",
            "Reconnected",
        )

    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="events",
    )

    exam_question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
    )

    event_type = models.CharField(
        max_length=30,
        choices=EventType.choices,
    )

    payload = models.JSONField(
        default=dict,
        blank=True,
    )

    occurred_at = models.DateTimeField(
        default=timezone.now,
    )

    class Meta:
        ordering = [
            "occurred_at",
            "id",
        ]

        indexes = [
            models.Index(
                fields=[
                    "attempt",
                    "occurred_at",
                ],
                name="event_attempt_time_idx",
            ),
            models.Index(
                fields=[
                    "event_type",
                ],
                name="event_type_idx",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.exam_question_id
            and self.attempt.exam_id
            != self.exam_question.exam_id
        ):
            raise ValidationError(
                {
                    "exam_question": (
                        "Event question must belong "
                        "to the attempt's exam."
                    )
                }
            )

    def __str__(self):
        return (
            f"{self.attempt_id} - "
            f"{self.event_type}"
        )