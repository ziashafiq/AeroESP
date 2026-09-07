from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import StudentProfile, TeacherProfile


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
def revoke_reviewer_access_on_rejection(sender, instance, **kwargs):
    """
    Withdraw expert-reviewer access when a teacher is rejected.

    This handler used to do the opposite as well: approving a teacher
    auto-created an ExpertReviewerProfile with is_active_reviewer=True.
    That conflated two decisions that are not the same question -
    "is this person a legitimate teacher?" and "do I want this person
    grading research items?" - and it granted the second silently as a
    side effect of answering the first. Granting reviewer status is now
    an explicit admin action; see the "Promote to expert reviewer"
    action on TeacherProfile in accounts/admin.py.

    The revocation half is deliberately kept, and the asymmetry is the
    point: this direction can only ever remove access, never hand it
    out, so it cannot grant a privilege behind the admin's back. A
    teacher whose approval has been withdrawn should not keep reviewing
    on the strength of an approval that no longer stands. Re-approving
    them does NOT restore reviewer access - that takes the explicit
    action again.

    Imported lazily so accounts does not import research_review at
    module load time - the dependency only exists inside this handler.
    """

    if (
        instance.approval_status
        != TeacherProfile.ApprovalStatus.REJECTED
    ):
        return

    from research_review.models import ExpertReviewerProfile

    ExpertReviewerProfile.objects.filter(
        user=instance.user,
    ).update(
        is_active_reviewer=False,
    )