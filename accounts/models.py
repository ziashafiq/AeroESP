from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    email = models.EmailField(
        unique=True,
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

    def __str__(self):
        return f"{self.user.username} - {self.code}"