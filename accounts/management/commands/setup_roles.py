from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from accounts.models import StudentProfile, TeacherProfile


class Command(BaseCommand):
    help = "Create AeroESP role groups and sync existing users."

    def handle(self, *args, **options):
        students_group, _ = Group.objects.get_or_create(
            name="Students"
        )

        teachers_group, _ = Group.objects.get_or_create(
            name="Teachers"
        )

        student_count = 0
        teacher_count = 0

        for profile in StudentProfile.objects.select_related("user"):
            profile.user.groups.add(students_group)
            profile.user.groups.remove(teachers_group)
            student_count += 1

        for profile in TeacherProfile.objects.select_related("user"):
            profile.user.groups.add(teachers_group)
            profile.user.groups.remove(students_group)
            teacher_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"AeroESP groups ready. "
                f"Students synced: {student_count}, "
                f"Teachers synced: {teacher_count}"
            )
        )