from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from accounts.models import StudentProfile, TeacherProfile


class Command(BaseCommand):
    help = "Create AeroESP role groups, permissions, and sync users."

    def handle(self, *args, **options):

        students_group, _ = Group.objects.get_or_create(
            name="Students"
        )

        teachers_group, _ = Group.objects.get_or_create(
            name="Teachers"
        )

        # ---------------------------------------------
        # Question permissions
        # ---------------------------------------------

        question_permissions = Permission.objects.filter(
            content_type__app_label="assessment",
            content_type__model="question",
        )

        teacher_allowed_codenames = {
            "view_question",
            "add_question",
            "change_question",
        }

        teacher_permissions = question_permissions.filter(
            codename__in=teacher_allowed_codenames
        )

        # Teachers can view/add/change questions.
        # Delete is intentionally NOT granted.
        teachers_group.permissions.remove(
            *question_permissions
        )

        teachers_group.permissions.add(
            *teacher_permissions
        )

        # Students must have no Question model permissions.
        students_group.permissions.remove(
            *question_permissions
        )

        # ---------------------------------------------
        # Sync existing users
        # ---------------------------------------------

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
                "AeroESP roles ready. "
                f"Students synced: {student_count}. "
                f"Teachers synced: {teacher_count}."
            )
        )