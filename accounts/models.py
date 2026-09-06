from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):

    # Unique, but nullable: users created outside the sign-up flow
    # (fixtures, imports, management commands) may have no email at all,
    # and several empty strings would collide on the unique index.
    email = models.EmailField(
        unique=True,
        null=True,
        blank=True,
    )

    email_verified = models.BooleanField(
        default=False,
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        null=True,
        blank=True,
    )

    ROLE_CHOICES = [
        ("STUDENT", "Student"),
        ("TEACHER", "Teacher"),
    ]

    selected_role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="STUDENT",
    )

    def save(self, *args, **kwargs):

        # Store "no email" as NULL so the unique index stays satisfiable.
        if not self.email:
            self.email = None

        return super().save(*args, **kwargs)

    def __str__(self):
        return self.username


class StudentProfile(models.Model):

    class AerospaceField(models.TextChoices):
        GENERAL = "GENERAL", "General Aerospace Engineering"
        AERODYNAMICS = "AERODYNAMICS", "Aerodynamics"
        FLIGHT_DYNAMICS_CONTROL = (
            "FLIGHT_DYNAMICS_CONTROL",
            "Flight Dynamics & Control",
        )
        PROPULSION = "PROPULSION", "Propulsion"
        STRUCTURES = "STRUCTURES", "Aerospace Structures"
        SPACE = "SPACE", "Space Engineering"
        OTHER = "OTHER", "Other"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    student_id = models.CharField(
        max_length=50,
        blank=True,
    )

    university = models.CharField(
        max_length=200,
        blank=True,
    )

    department = models.CharField(
        max_length=200,
        default="Aerospace Engineering",
    )

    primary_aerospace_field = models.CharField(
        max_length=40,
        choices=AerospaceField.choices,
        default=AerospaceField.GENERAL,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Student: {self.user.username}"


class TeacherProfile(models.Model):

    class ApprovalStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
    )

    university = models.CharField(
        max_length=200,
        blank=True,
    )

    department = models.CharField(
        max_length=200,
        blank=True,
    )

    academic_email = models.EmailField(
        blank=True,
    )

    approval_status = models.CharField(
        max_length=20,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.PENDING,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_teacher_profiles",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_approved(self):
        return self.approval_status == self.ApprovalStatus.APPROVED

    def __str__(self):
        return f"Teacher: {self.user.username}"


class EmailVerificationCode(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="email_verification_codes",
    )

    code = models.CharField(
        max_length=6,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField()

    is_used = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ("-created_at",)

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()

    def is_valid(self):
        return not self.is_used and not self.is_expired

    def __str__(self):
        return f"{self.user.username} - {self.code}"


class CaptchaChallenge(models.Model):
    """
    One pending registration captcha.

    The answer is kept only as a keyed hash; the rendered PNG is stored
    so the image view can serve it without holding the plain answer
    anywhere. Rows are consumed on the first attempt and expired rows
    are swept whenever a new challenge is issued.
    """

    key = models.CharField(
        max_length=40,
        unique=True,
        db_index=True,
    )

    answer_hash = models.CharField(
        max_length=64,
    )

    # One rendering per theme: a PNG cannot follow the viewer's
    # appearance setting, and the light one is a white slab inside a
    # dark card.
    image = models.BinaryField()

    image_dark = models.BinaryField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    expires_at = models.DateTimeField(
        db_index=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"captcha {self.key[:8]}"