from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import (
    get_user_model,
)
from django.contrib.auth.models import (
    Group,
)
from django.core.exceptions import (
    ValidationError,
)
from django.core.management import (
    call_command,
)
from django.test import TestCase
from django.utils import timezone

from assessment.models import Question

from .models import (
    Exam,
    ExamAttempt,
    ExamEvent,
    ExamQuestion,
)

from .student_forms import (
    ExamAccessCodeForm,
)

from .student_views import (
    _deadline_passed,
    _finalize_attempt,
    _result_is_visible,
    _save_answer,
    _snapshot_correct_choice,
    _start_attempt,
)

from .views import (
    _publish_exam,
)


class StudentExamRunnerTests(
    TestCase
):

    @classmethod
    def setUpTestData(cls):

        call_command(
            "bootstrap_aeroesp_demo",
            stdout=StringIO(),
        )

        cls.User = (
            get_user_model()
        )

        cls.teachers_group, _ = (
            Group.objects.get_or_create(
                name="Teachers",
            )
        )

        cls.students_group, _ = (
            Group.objects.get_or_create(
                name="Students",
            )
        )

        cls.teacher = (
            cls.User.objects
            .create_user(
                username=(
                    "runner_teacher"
                ),
                email=(
                    "runner_teacher"
                    "@test.local"
                ),
                password=(
                    "TeacherPass123!"
                ),
            )
        )

        cls.teacher.groups.add(
            cls.teachers_group
        )

        cls.student = (
            cls.User.objects
            .create_user(
                username=(
                    "runner_student"
                ),
                email=(
                    "runner_student"
                    "@test.local"
                ),
                password=(
                    "StudentPass123!"
                ),
            )
        )

        cls.student.groups.add(
            cls.students_group
        )

        questions = list(
            Question.objects
            .order_by(
                "pk"
            )[:3]
        )

        if len(questions) < 3:
            raise RuntimeError(
                "Student Runner tests "
                "require at least three "
                "questions."
            )

        cls.question_1 = (
            questions[0]
        )

        cls.question_2 = (
            questions[1]
        )

        cls.question_3 = (
            questions[2]
        )


    def create_draft_exam(
        self,
        *,
        title="Runner Exam",
        duration_minutes=60,
        max_attempts=2,
        result_policy=(
            Exam.ResultPolicy.IMMEDIATE
        ),
        starts_at=None,
        ends_at=None,
    ):

        now = timezone.now()

        return Exam.objects.create(
            owner=self.teacher,
            title=title,
            duration_minutes=(
                duration_minutes
            ),
            max_attempts=(
                max_attempts
            ),
            result_policy=(
                result_policy
            ),
            status=Exam.Status.DRAFT,
            starts_at=(
                starts_at
                if starts_at
                is not None
                else (
                    now
                    - timedelta(
                        minutes=5
                    )
                )
            ),
            ends_at=(
                ends_at
                if ends_at
                is not None
                else (
                    now
                    + timedelta(
                        hours=2
                    )
                )
            ),
        )


    def add_question(
        self,
        *,
        exam,
        question,
        order,
        points,
    ):

        return (
            ExamQuestion.objects
            .create(
                exam=exam,
                question=question,
                order=order,
                points=points,
                required=True,
                question_version=(
                    getattr(
                        question,
                        "version",
                        1,
                    )
                    or 1
                ),
            )
        )


    def create_published_exam(
        self,
        *,
        max_attempts=2,
        duration_minutes=60,
        result_policy=(
            Exam.ResultPolicy.IMMEDIATE
        ),
        ends_at=None,
    ):

        exam = (
            self.create_draft_exam(
                duration_minutes=(
                    duration_minutes
                ),
                max_attempts=(
                    max_attempts
                ),
                result_policy=(
                    result_policy
                ),
                ends_at=ends_at,
            )
        )

        self.add_question(
            exam=exam,
            question=(
                self.question_1
            ),
            order=1,
            points=Decimal(
                "2.00"
            ),
        )

        self.add_question(
            exam=exam,
            question=(
                self.question_2
            ),
            order=2,
            points=Decimal(
                "3.00"
            ),
        )

        return _publish_exam(
            exam
        )


    # =====================================================
    # Start lifecycle
    # =====================================================

    def test_draft_exam_cannot_start(
        self,
    ):

        exam = (
            self.create_draft_exam()
        )

        with self.assertRaises(
            ValidationError
        ):
            _start_attempt(
                exam,
                self.student,
            )


    def test_start_creates_attempt_answers_and_event(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        attempt, created = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        self.assertTrue(
            created
        )

        self.assertEqual(
            attempt.status,
            ExamAttempt.Status
            .IN_PROGRESS,
        )

        self.assertEqual(
            attempt.attempt_number,
            1,
        )

        self.assertEqual(
            attempt.answers.count(),
            2,
        )

        event = (
            attempt.events
            .get(
                event_type=(
                    ExamEvent.EventType
                    .ATTEMPT_STARTED
                )
            )
        )

        self.assertIn(
            "presentation",
            event.payload,
        )

        presentation = (
            event.payload[
                "presentation"
            ]
        )

        self.assertEqual(
            len(
                presentation[
                    "question_order"
                ]
            ),
            2,
        )


    def test_start_returns_existing_active_attempt(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        attempt_1, created_1 = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        attempt_2, created_2 = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        self.assertTrue(
            created_1
        )

        self.assertFalse(
            created_2
        )

        self.assertEqual(
            attempt_1.pk,
            attempt_2.pk,
        )

        self.assertEqual(
            ExamAttempt.objects
            .filter(
                exam=exam,
                student=self.student,
            )
            .count(),
            1,
        )


    def test_maximum_attempt_limit_is_enforced(
        self,
    ):

        exam = (
            self.create_published_exam(
                max_attempts=1,
            )
        )

        attempt, _ = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        _finalize_attempt(
            attempt,
            auto_submit=False,
        )

        with self.assertRaises(
            ValidationError
        ):
            _start_attempt(
                exam,
                self.student,
            )


    def test_exam_close_time_caps_deadline(
        self,
    ):

        exam_close = (
            timezone.now()
            + timedelta(
                minutes=3
            )
        )

        exam = (
            self.create_published_exam(
                duration_minutes=60,
                ends_at=exam_close,
            )
        )

        attempt, _ = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        self.assertEqual(
            attempt.deadline_at,
            exam_close,
        )


    # =====================================================
    # Answer saving
    # =====================================================

    def test_correct_answer_is_scored_from_snapshot(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        attempt, _ = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        item = (
            exam.exam_questions
            .order_by(
                "order"
            )
            .first()
        )

        correct_choice = (
            _snapshot_correct_choice(
                item
            )
        )

        self.assertIn(
            correct_choice,
            {
                "A",
                "B",
                "C",
                "D",
            },
        )

        answer = _save_answer(
            attempt,
            item,
            correct_choice,
            1000,
        )

        self.assertTrue(
            answer.is_correct
        )

        self.assertEqual(
            answer.awarded_points,
            item.points,
        )

        self.assertEqual(
            answer.time_spent_ms,
            1000,
        )

        self.assertTrue(
            ExamEvent.objects
            .filter(
                attempt=attempt,
                exam_question=item,
                event_type=(
                    ExamEvent.EventType
                    .ANSWER_SAVED
                ),
            )
            .exists()
        )


    def test_answer_change_count_and_time_are_accumulated(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        attempt, _ = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        item = (
            exam.exam_questions
            .order_by(
                "order"
            )
            .first()
        )

        correct_choice = (
            _snapshot_correct_choice(
                item
            )
        )

        wrong_choice = next(
            choice
            for choice
            in (
                "A",
                "B",
                "C",
                "D",
            )
            if choice
            != correct_choice
        )

        _save_answer(
            attempt,
            item,
            wrong_choice,
            1000,
        )

        answer = _save_answer(
            attempt,
            item,
            correct_choice,
            1500,
        )

        self.assertEqual(
            answer.answer_change_count,
            1,
        )

        self.assertEqual(
            answer.time_spent_ms,
            2500,
        )

        self.assertTrue(
            answer.is_correct
        )

        self.assertTrue(
            ExamEvent.objects
            .filter(
                attempt=attempt,
                exam_question=item,
                event_type=(
                    ExamEvent.EventType
                    .ANSWER_CHANGED
                ),
            )
            .exists()
        )


    def test_invalid_answer_choice_is_rejected(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        attempt, _ = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        item = (
            exam.exam_questions
            .first()
        )

        with self.assertRaises(
            ValidationError
        ):
            _save_answer(
                attempt,
                item,
                "X",
                100,
            )


    # =====================================================
    # Final scoring / submission
    # =====================================================

    def test_finalize_attempt_calculates_score(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        attempt, _ = (
            _start_attempt(
                exam,
                self.student,
            )
        )

        items = list(
            exam.exam_questions
            .order_by(
                "order"
            )
        )

        first_correct = (
            _snapshot_correct_choice(
                items[0]
            )
        )

        second_correct = (
            _snapshot_correct_choice(
                items[1]
            )
        )

        second_wrong = next(
            choice
            for choice
            in (
                "A",
                "B",
                "C",
                "D",
            )
            if choice
            != second_correct
        )

        _save_answer(
            attempt,
            items[0],
            first_correct,
            1000,
        )

        _save_answer(
            attempt,
            items[1],
            second_wrong,
            1000,
        )

        attempt = (
            _finalize_attempt(
                attempt,
                auto_submit=False,
            )
        )

        self.assertEqual(
            attempt.status,
            ExamAttempt.Status
            .SUBMITTED,
        )

        self.assertEqual(
            attempt.score,
            Decimal(
                "2.00"
            ),
        )

        self.assertEqual(
            attempt.max_score,
            Decimal(
                "5.00"
            ),
        )

        self.assertEqual(
            attempt.percentage,
            Decimal(
                "40.00"
            ),
        )

        self.assertIsNotNone(
            attempt.submitted_at
        )

        self.assertTrue(
            ExamEvent.objects
            .filter(
                attempt=attempt,
                event_type=(
                    ExamEvent.EventType
                    .SUBMITTED
                ),
            )
            .exists()
        )


    def test_auto_submit_sets_correct_status(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        now = timezone.now()

        past_started_at = (
            now
            - timedelta(
                minutes=2
            )
        )

        past_deadline = (
            now
            - timedelta(
                minutes=1
            )
        )

        ExamAttempt.objects.filter(
            pk=attempt.pk,
        ).update(
            started_at=(
                past_started_at
            ),
            deadline_at=(
                past_deadline
            ),
        )

        ExamAttempt.objects.filter(
            pk=attempt.pk,
        ).update(
            deadline_at=(
                past_deadline
            )
        )

        attempt.refresh_from_db()

        self.assertTrue(
            _deadline_passed(
                attempt
            )
        )

        attempt = (
            _finalize_attempt(
                attempt,
                auto_submit=True,
            )
        )

        self.assertEqual(
            attempt.status,
            ExamAttempt.Status
            .AUTO_SUBMITTED,
        )

        self.assertTrue(
            ExamEvent.objects
            .filter(
                attempt=attempt,
                event_type=(
                    ExamEvent.EventType
                    .AUTO_SUBMITTED
                ),
            )
            .exists()
        )


    # =====================================================
    # Access code / result policy
    # =====================================================

    def test_access_code_is_case_insensitive(
        self,
    ):

        exam = (
            self.create_published_exam()
        )

        form = ExamAccessCodeForm(
            data={
                "code": (
                    exam.access_code
                    .lower()
                )
            }
        )

        self.assertTrue(
            form.is_valid(),
            form.errors,
        )

        self.assertEqual(
            form.exam.pk,
            exam.pk,
        )


    def test_immediate_result_policy_is_visible(
        self,
    ):

        exam = (
            self.create_published_exam(
                result_policy=(
                    Exam.ResultPolicy
                    .IMMEDIATE
                ),
            )
        )

        self.assertTrue(
            _result_is_visible(
                exam
            )
        )


    def test_after_close_result_policy(
        self,
    ):

        exam = (
            self.create_published_exam(
                result_policy=(
                    Exam.ResultPolicy
                    .AFTER_CLOSE
                ),
            )
        )

        self.assertFalse(
            _result_is_visible(
                exam
            )
        )

        exam.ends_at = (
            timezone.now()
            - timedelta(
                seconds=1
            )
        )

        self.assertTrue(
            _result_is_visible(
                exam
            )
        )