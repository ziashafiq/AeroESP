from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db.models import F

from accounts.models import (
    StudentProfile,
)

from assessment.models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


class Command(BaseCommand):

    help = (
        "Audit AeroESP Foundation v1 architecture, "
        "permissions, taxonomy, ownership, and demo data."
    )

    def handle(self, *args, **options):

        failures = []

        # =================================================
        # Helper
        # =================================================

        def check(
            condition,
            success_message,
            failure_message,
        ):

            if condition:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"[PASS] {success_message}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.ERROR(
                        f"[FAIL] {failure_message}"
                    )
                )

                failures.append(
                    failure_message
                )

        # =================================================
        # Custom User
        # =================================================

        User = get_user_model()

        check(
            settings.AUTH_USER_MODEL
            == "accounts.CustomUser",
            "AUTH_USER_MODEL uses accounts.CustomUser.",
            "AUTH_USER_MODEL is not accounts.CustomUser.",
        )

        check(
            User._meta.label
            == "accounts.CustomUser",
            "Django resolves the custom user correctly.",
            "Django is resolving the wrong user model.",
        )

        # =================================================
        # Groups
        # =================================================

        students_group = (
            Group.objects.filter(
                name="Students"
            ).first()
        )

        teachers_group = (
            Group.objects.filter(
                name="Teachers"
            ).first()
        )

        check(
            students_group is not None,
            "Students group exists.",
            "Students group does not exist.",
        )

        check(
            teachers_group is not None,
            "Teachers group exists.",
            "Teachers group does not exist.",
        )

        # =================================================
        # Group Permissions
        # =================================================

        if teachers_group:

            teacher_question_permissions = set(
                teachers_group.permissions.filter(
                    content_type__app_label="assessment",
                    content_type__model="question",
                ).values_list(
                    "codename",
                    flat=True,
                )
            )

            expected = {
                "view_question",
                "add_question",
                "change_question",
            }

            check(
                expected.issubset(
                    teacher_question_permissions
                ),
                (
                    "Teachers have view/add/change "
                    "Question permissions."
                ),
                (
                    "Teacher Question permissions "
                    "are incomplete."
                ),
            )

            check(
                "delete_question"
                not in teacher_question_permissions,
                (
                    "Teachers do not have direct "
                    "Question delete permission."
                ),
                (
                    "Teachers unexpectedly have "
                    "delete_question permission."
                ),
            )

        if students_group:

            student_question_permissions = (
                students_group.permissions.filter(
                    content_type__app_label="assessment",
                    content_type__model="question",
                ).count()
            )

            check(
                student_question_permissions == 0,
                (
                    "Students have no direct "
                    "Question permissions."
                ),
                (
                    "Students unexpectedly have "
                    "Question permissions."
                ),
            )

        # =================================================
        # Taxonomy
        # =================================================

        domain_count = (
            AerospaceDomain.objects.count()
        )

        topic_count = (
            AerospaceTopic.objects.count()
        )

        check(
            domain_count == 12,
            "Exactly 12 aerospace domains exist.",
            (
                f"Expected 12 aerospace domains, "
                f"found {domain_count}."
            ),
        )

        check(
            topic_count >= 100,
            (
                f"Taxonomy contains {topic_count} "
                "aerospace topics."
            ),
            (
                f"Taxonomy has only {topic_count} topics."
            ),
        )

        # =================================================
        # Hierarchical Consistency
        # =================================================

        invalid_parent_count = (
            AerospaceTopic.objects
            .filter(
                parent__isnull=False
            )
            .exclude(
                parent__domain=F("domain")
            )
            .count()
        )

        check(
            invalid_parent_count == 0,
            (
                "All parent topics belong to "
                "the correct domain."
            ),
            (
                f"{invalid_parent_count} topic(s) "
                "have a parent from another domain."
            ),
        )

        # =================================================
        # Topic Workflow Consistency
        # =================================================

        pending_active = (
            AerospaceTopic.objects.filter(
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .PENDING
                ),
                is_active=True,
            ).count()
        )

        rejected_active = (
            AerospaceTopic.objects.filter(
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .REJECTED
                ),
                is_active=True,
            ).count()
        )

        approved_inactive = (
            AerospaceTopic.objects.filter(
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .APPROVED
                ),
                is_active=False,
            ).count()
        )

        check(
            pending_active == 0,
            "Pending topics are inactive.",
            (
                f"{pending_active} pending topic(s) "
                "are incorrectly active."
            ),
        )

        check(
            rejected_active == 0,
            "Rejected topics are inactive.",
            (
                f"{rejected_active} rejected topic(s) "
                "are incorrectly active."
            ),
        )

        check(
            approved_inactive == 0,
            "Approved topics are active.",
            (
                f"{approved_inactive} approved topic(s) "
                "are incorrectly inactive."
            ),
        )

        # =================================================
        # Question / Topic Consistency
        # =================================================

        invalid_question_taxonomy = (
            Question.objects
            .filter(
                domain_ref__isnull=False,
                topic_ref__isnull=False,
            )
            .exclude(
                topic_ref__domain=F(
                    "domain_ref"
                )
            )
            .count()
        )

        check(
            invalid_question_taxonomy == 0,
            (
                "All questions use topics from "
                "their selected domain."
            ),
            (
                f"{invalid_question_taxonomy} question(s) "
                "have mismatched domain/topic."
            ),
        )

        # =================================================
        # Ownership
        # =================================================

        student_user_ids = (
            StudentProfile.objects.values_list(
                "user_id",
                flat=True,
            )
        )

        student_owned_questions = (
            Question.objects.filter(
                owner_id__in=student_user_ids
            ).count()
        )

        check(
            student_owned_questions == 0,
            "No Question is owned by a Student.",
            (
                f"{student_owned_questions} question(s) "
                "are incorrectly owned by students."
            ),
        )

        # =================================================
        # Demo Data
        # =================================================

        demo100_count = (
            Question.objects.filter(
                source_reference__startswith=(
                    "DEMO100::"
                )
            ).count()
        )

        check(
            demo100_count == 100,
            "Exactly 100 structured Demo100 questions exist.",
            (
                f"Expected 100 Demo100 questions, "
                f"found {demo100_count}."
            ),
        )

        # =================================================
        # Result
        # =================================================

        self.stdout.write("")

        if failures:

            self.stdout.write(
                self.style.ERROR(
                    "AeroESP Foundation Audit FAILED."
                )
            )

            self.stdout.write(
                self.style.ERROR(
                    f"Failures: {len(failures)}"
                )
            )

            raise CommandError(
                "Foundation audit detected problems."
            )

        self.stdout.write(
            self.style.SUCCESS(
                "AeroESP Foundation v1 Audit: PASS"
            )
        )