from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.db.models import (
    Count,
    F,
    Q,
)

from exams.models import (
    Exam,
    ExamAttempt,
    ExamEvent,
    StudentAnswer,
)


class Command(BaseCommand):

    help = (
        "Audit AeroESP Exam Engine "
        "data integrity."
    )

    def handle(
        self,
        *args,
        **options,
    ):

        failures = []

        def check(
            condition,
            message,
        ):

            if condition:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"[PASS] {message}"
                    )
                )

            else:
                failures.append(
                    message
                )

                self.stdout.write(
                    self.style.ERROR(
                        f"[FAIL] {message}"
                    )
                )

        invalid_exam_owner = (
            Exam.objects
            .exclude(
                Q(
                    owner__groups__name=(
                        "Teachers"
                    )
                )
                |
                Q(
                    owner__is_superuser=True
                )
            )
            .distinct()
            .exists()
        )

        check(
            not invalid_exam_owner,
            (
                "All Exam owners are "
                "Teachers or superusers."
            ),
        )

        invalid_attempt_user = (
            ExamAttempt.objects
            .exclude(
                student__groups__name=(
                    "Students"
                )
            )
            .distinct()
            .exists()
        )

        check(
            not invalid_attempt_user,
            (
                "All ExamAttempt users "
                "belong to Students."
            ),
        )

        over_limit_attempt = (
            ExamAttempt.objects
            .filter(
                attempt_number__gt=F(
                    "exam__max_attempts"
                )
            )
            .exists()
        )

        check(
            not over_limit_attempt,
            (
                "No attempt number exceeds "
                "its Exam max_attempts."
            ),
        )

        duplicate_active = (
            ExamAttempt.objects
            .filter(
                status=(
                    ExamAttempt.Status
                    .IN_PROGRESS
                )
            )
            .values(
                "exam_id",
                "student_id",
            )
            .annotate(
                count=Count("id")
            )
            .filter(
                count__gt=1
            )
            .exists()
        )

        check(
            not duplicate_active,
            (
                "No student has multiple "
                "active attempts for the "
                "same Exam."
            ),
        )

        mismatched_answer = (
            StudentAnswer.objects
            .exclude(
                attempt__exam_id=F(
                    "exam_question__exam_id"
                )
            )
            .exists()
        )

        check(
            not mismatched_answer,
            (
                "All StudentAnswers belong "
                "to the Attempt Exam."
            ),
        )

        excessive_points = (
            StudentAnswer.objects
            .filter(
                awarded_points__gt=F(
                    "exam_question__points"
                )
            )
            .exists()
        )

        check(
            not excessive_points,
            (
                "No StudentAnswer exceeds "
                "the Question point value."
            ),
        )

        mismatched_event = (
            ExamEvent.objects
            .filter(
                exam_question__isnull=False,
            )
            .exclude(
                attempt__exam_id=F(
                    "exam_question__exam_id"
                )
            )
            .exists()
        )

        check(
            not mismatched_event,
            (
                "All question-linked "
                "ExamEvents belong to the "
                "Attempt Exam."
            ),
        )

        published = (
            Exam.objects.filter(
                status=(
                    Exam.Status.PUBLISHED
                )
            )
        )

        published_without_items = (
            published
            .annotate(
                question_count=Count(
                    "exam_questions"
                )
            )
            .filter(
                question_count=0
            )
            .exists()
        )

        check(
            not published_without_items,
            (
                "Every published Exam "
                "contains at least one "
                "question."
            ),
        )

        missing_access_code = (
            published
            .filter(
                Q(
                    access_code__isnull=True
                )
                |
                Q(
                    access_code=""
                )
            )
            .exists()
        )

        check(
            not missing_access_code,
            (
                "Every published Exam "
                "has an access code."
            ),
        )

        missing_published_time = (
            published
            .filter(
                published_at__isnull=True
            )
            .exists()
        )

        check(
            not missing_published_time,
            (
                "Every published Exam "
                "has published_at."
            ),
        )

        missing_snapshot = (
            published
            .filter(
                exam_questions__snapshot={}
            )
            .exists()
        )

        check(
            not missing_snapshot,
            (
                "Every published Exam "
                "question has a frozen "
                "snapshot."
            ),
        )

        if failures:

            raise CommandError(
                (
                    "AeroESP Exam Engine "
                    f"Audit: FAIL "
                    f"({len(failures)} issue(s))"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "AeroESP Exam Engine "
                    "Audit: PASS"
                )
            )
        )