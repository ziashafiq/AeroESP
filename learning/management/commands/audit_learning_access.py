from django.contrib.auth import get_user_model
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from accounts.models import (
    StudentProfile,
    TeacherProfile,
)

from intelligence.models import (
    GeneratedQuestionDraft,
    LearnerInsightSnapshot,
    QuestionAISuggestion,
)

from learning.models import (
    Enrollment,
    LearningCourse,
    LearningEvent,
    LearningProgress,
    PlacementAttempt,
)


User = get_user_model()


class Command(BaseCommand):

    help = (
        "Audit AeroESP learning, role, "
        "analytics, and AI access integrity."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        failures = []

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

                failures.append(
                    failure_message
                )

                self.stdout.write(
                    self.style.ERROR(
                        f"[FAIL] {failure_message}"
                    )
                )

        # =================================================
        # Role overlap
        # =================================================

        dual_role_users = (
            User.objects
            .filter(
                groups__name="Students"
            )
            .filter(
                groups__name="Teachers"
            )
            .distinct()
        )

        check(
            not dual_role_users.exists(),
            (
                "No user belongs to both "
                "Students and Teachers."
            ),
            (
                "Some users belong to both "
                "Students and Teachers."
            ),
        )

        # =================================================
        # Student profile → Students group
        # =================================================

        invalid_student_profiles = (
            StudentProfile.objects
            .exclude(
                user__groups__name="Students"
            )
        )

        check(
            not invalid_student_profiles.exists(),
            (
                "All StudentProfile users belong "
                "to the Students group."
            ),
            (
                "Some StudentProfile users are "
                "missing the Students group."
            ),
        )

        # =================================================
        # Approved teacher → Teachers group
        # =================================================

        approved_teacher_profiles = (
            TeacherProfile.objects
            .filter(
                approval_status=(
                    TeacherProfile
                    .ApprovalStatus
                    .APPROVED
                )
            )
        )

        invalid_teacher_profiles = (
            approved_teacher_profiles
            .exclude(
                user__groups__name="Teachers"
            )
        )

        check(
            not invalid_teacher_profiles.exists(),
            (
                "All approved teachers belong "
                "to the Teachers group."
            ),
            (
                "Some approved teachers are "
                "missing the Teachers group."
            ),
        )

        # =================================================
        # Learning course ownership
        # =================================================

        invalid_courses = []

        for course in (
            LearningCourse.objects
            .select_related(
                "created_by",
                "created_by__teacher_profile",
            )
        ):

            owner = course.created_by

            if owner.is_superuser:
                continue

            profile = getattr(
                owner,
                "teacher_profile",
                None,
            )

            if (
                profile is None
                or not profile.is_approved
            ):
                invalid_courses.append(
                    course.pk
                )

        check(
            not invalid_courses,
            (
                "All LearningCourse owners are "
                "approved teachers or superusers."
            ),
            (
                "Invalid LearningCourse owners: "
                f"{invalid_courses}"
            ),
        )

        # =================================================
        # Enrollment role
        # =================================================

        invalid_enrollments = (
            Enrollment.objects
            .exclude(
                student__groups__name="Students"
            )
        )

        check(
            not invalid_enrollments.exists(),
            (
                "All Enrollment students belong "
                "to the Students group."
            ),
            (
                "Some Enrollment records belong "
                "to non-student users."
            ),
        )

        # =================================================
        # LearningProgress role
        # =================================================

        invalid_progress = (
            LearningProgress.objects
            .exclude(
                student__groups__name="Students"
            )
        )

        check(
            not invalid_progress.exists(),
            (
                "All LearningProgress records "
                "belong to Students."
            ),
            (
                "Some LearningProgress records "
                "belong to non-student users."
            ),
        )

        # =================================================
        # Placement role
        # =================================================

        invalid_placement = (
            PlacementAttempt.objects
            .exclude(
                student__groups__name="Students"
            )
        )

        check(
            not invalid_placement.exists(),
            (
                "All PlacementAttempt records "
                "belong to Students."
            ),
            (
                "Some PlacementAttempt records "
                "belong to non-student users."
            ),
        )

        # =================================================
        # Research events
        # =================================================

        invalid_events = (
            LearningEvent.objects
            .exclude(
                student__groups__name="Students"
            )
        )

        check(
            not invalid_events.exists(),
            (
                "All research learning events "
                "belong to Students."
            ),
            (
                "Some LearningEvent records "
                "belong to non-student users."
            ),
        )

        # =================================================
        # AI generated draft ownership
        # =================================================

        invalid_drafts = []

        for draft in (
            GeneratedQuestionDraft.objects
            .select_related(
                "created_by",
                "created_by__teacher_profile",
            )
        ):

            owner = draft.created_by

            if owner.is_superuser:
                continue

            profile = getattr(
                owner,
                "teacher_profile",
                None,
            )

            if (
                profile is None
                or not profile.is_approved
            ):
                invalid_drafts.append(
                    draft.pk
                )

        check(
            not invalid_drafts,
            (
                "All AI-generated drafts are "
                "owned by approved teachers "
                "or superusers."
            ),
            (
                "Invalid AI draft owners: "
                f"{invalid_drafts}"
            ),
        )

        # =================================================
        # AI suggestion creator
        # =================================================

        invalid_suggestions = []

        suggestions = (
            QuestionAISuggestion.objects
            .exclude(created_by=None)
            .select_related(
                "created_by",
                "created_by__teacher_profile",
            )
        )

        for suggestion in suggestions:

            owner = suggestion.created_by

            if owner.is_superuser:
                continue

            profile = getattr(
                owner,
                "teacher_profile",
                None,
            )

            if (
                profile is None
                or not profile.is_approved
            ):
                invalid_suggestions.append(
                    suggestion.pk
                )

        check(
            not invalid_suggestions,
            (
                "AI question suggestions have "
                "valid creators."
            ),
            (
                "Invalid AI suggestion creators: "
                f"{invalid_suggestions}"
            ),
        )

        # =================================================
        # AI learner insight ownership target
        # =================================================

        invalid_insights = (
            LearnerInsightSnapshot.objects
            .exclude(
                student__groups__name="Students"
            )
        )

        check(
            not invalid_insights.exists(),
            (
                "All learner insight snapshots "
                "belong to Students."
            ),
            (
                "Some learner insight snapshots "
                "belong to non-student users."
            ),
        )

        # =================================================
        # Result
        # =================================================

        if failures:

            raise CommandError(
                "AeroESP runtime access audit "
                f"failed with {len(failures)} "
                "issue(s)."
            )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "AeroESP Learning / AI "
                "Runtime Access Audit: PASS"
            )
        )