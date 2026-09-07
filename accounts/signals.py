from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StudentProfile, TeacherProfile


REVIEWER_DEFAULT_DISCIPLINE = "AEROSPACE"


@receiver(post_save, sender=StudentProfile)
def sync_student_group(sender, instance, **kwargs):
    students_group, _ = Group.objects.get_or_create(
        name="Students"
    )

    teachers_group, _ = Group.objects.get_or_create(
        name="Teachers"
    )

    instance.user.groups.add(students_group)
    instance.user.groups.remove(teachers_group)


@receiver(post_save, sender=TeacherProfile)
def sync_teacher_group(sender, instance, **kwargs):
    students_group, _ = Group.objects.get_or_create(
        name="Students"
    )

    teachers_group, _ = Group.objects.get_or_create(
        name="Teachers"
    )

    instance.user.groups.add(teachers_group)
    instance.user.groups.remove(students_group)


@receiver(post_save, sender=TeacherProfile)
def sync_reviewer_access_with_approval(sender, instance, **kwargs):
    """
    Keep expert-reviewer access in step with teacher approval.

    research_review.ExpertReviewerProfile is a separate model with its
    own reviewer-specific fields (discipline, institution), and nothing
    ever created it: approving a teacher in the admin left them with no
    way to reach /expert-review/ at all, and the "Expert Review" sidebar
    link (gated on expert_reviewer_profile.is_active_reviewer) never
    appeared. An admin had to know to create the row by hand in a
    second, undocumented admin screen.

    Imported lazily so accounts does not import research_review at
    module load time - the dependency only exists inside this handler.
    """

    from research_review.models import ExpertReviewerProfile

    if (
        instance.approval_status
        == TeacherProfile.ApprovalStatus.APPROVED
    ):

        ExpertReviewerProfile.objects.get_or_create(
            user=instance.user,
            defaults={
                "discipline": REVIEWER_DEFAULT_DISCIPLINE,
                "institution": instance.university,
                "is_active_reviewer": True,
            },
        )

    elif (
        instance.approval_status
        == TeacherProfile.ApprovalStatus.REJECTED
    ):

        # A rejected teacher must not retain reviewer access from an
        # earlier approval.
        ExpertReviewerProfile.objects.filter(
            user=instance.user,
        ).update(
            is_active_reviewer=False,
        )