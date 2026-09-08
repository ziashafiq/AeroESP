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

    # Interface preference, not identity - but stored on the user
    # rather than only in localStorage so it follows them to a new
    # device or browser. Guests keep the same choice in localStorage;
    # see static/aeroesp/js/app.js.
    PALETTE_CHOICES = [
        ("skyline", "Skyline"),
        ("copper", "Copper"),
        ("indigo", "Indigo"),
        ("verdigris", "Verdigris"),
        ("slate", "Slate"),
    ]

    color_palette = models.CharField(
        max_length=20,
        choices=PALETTE_CHOICES,
        default="skyline",
    )

    # Set once, at registration, when the Terms of Use checkbox is
    # accepted. A timestamp rather than a boolean so acceptance of a
    # confidentiality agreement over exam content has evidence behind
    # it, not just an unlogged checkbox - this is what makes a breach
    # of the confidentiality terms something that can actually be
    # pursued.
    terms_accepted_at = models.DateTimeField(
        null=True,
        blank=True,
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


class HelpGuide(models.Model):
    """
    An admin-editable piece of onboarding/help content.

    Exists so that "how do I use this" documentation can be written and
    corrected by the site owner from the Django admin - text, an
    uploaded file (PDF, slides), or both - without touching code or
    asking a developer to redeploy for a wording fix.
    """

    class Audience(models.TextChoices):
        EVERYONE = "EVERYONE", "Everyone"
        STUDENT = "STUDENT", "Student"
        TEACHER = "TEACHER", "Teacher"
        EXPERT_REVIEWER = "EXPERT_REVIEWER", "Expert Reviewer"

    audience = models.CharField(
        max_length=20,
        choices=Audience.choices,
        default=Audience.EVERYONE,
        help_text=(
            "Who this guide is for. It appears on the public list for "
            "everyone, and is what the in-app Help icon matches "
            "against the signed-in user's role."
        ),
    )

    slug = models.SlugField(
        max_length=140,
        unique=True,
        help_text=(
            "Used in the guide's URL. "
            "'expert-reviewer-getting-started' is used automatically "
            "by the /expert-review/getting-started/ link if present."
        ),
    )

    title = models.CharField(
        max_length=200,
    )

    summary = models.CharField(
        max_length=300,
        blank=True,
        help_text="Short teaser shown next to the link on the list.",
    )

    body = models.TextField(
        blank=True,
        help_text=(
            "Plain text is fine - line breaks are preserved. Leave "
            "empty for a file-only guide."
        ),
    )

    attachment = models.FileField(
        upload_to="guides/",
        blank=True,
        null=True,
        help_text="Optional: a PDF or document to offer for download.",
    )

    is_published = models.BooleanField(
        default=True,
    )

    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first within the same audience.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("audience", "order", "title")

    def __str__(self):
        return f"{self.get_audience_display()} - {self.title}"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("help_detail", args=[self.slug])