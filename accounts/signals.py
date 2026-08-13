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