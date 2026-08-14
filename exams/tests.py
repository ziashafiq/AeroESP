from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from assessment.models import Question

from .models import (
    Exam,
    ExamAttempt,
    ExamEvent,
    ExamQuestion,
    StudentAnswer,
)


class ExamEngineModelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.User = get_user_model()

        cls.teachers_group, _ = Group.objects.get_or_create(
            name="Teachers",
        )

        cls.students_group, _ = Group.objects.get_or_create(
            name="Students",
        )

        cls.teacher = cls.User.objects.create_user(
            username="exam_teacher",
            email="exam_teacher@test.local",
            password="TeacherPass123!",
        )
        cls.teacher.groups.add(
            cls.teachers_group,
        )

        cls.teacher_2 = cls.User.objects.create_user(
            username="exam_teacher_2",
            email="exam_teacher_2@test.local",
            password="TeacherPass123!",
        )
        cls.teacher_2.groups.add(
            cls.teachers_group,
        )

        cls.student = cls.User.objects.create_user(
            username="exam_student",
            email="exam_student@test.local",
            password="StudentPass123!",
        )
        cls.student.groups.add(
            cls.students_group,
        )

        cls.student_2 = cls.User.objects.create_user(
            username="exam_student_2",
            email="exam_student_2@test.local",
            password="StudentPass123!",
        )
        cls.student_2.groups.add(
            cls.students_group,
        )

        cls.unassigned_user = cls.User.objects.create_user(
            username="unassigned_user",
            email="unassigned@test.local",
            password="UserPass123!",
        )

        # Reuse the already tested idempotent AeroESP bootstrap
        # command to create development taxonomy/questions.
        call_command(
            "bootstrap_aeroesp_demo",
            stdout=StringIO(),
        )

        questions = list(
            Question.objects.order_by("pk")[:3]
        )

        if len(questions) < 3:
            raise RuntimeError(
                "Exam tests require at least three questions."
            )

        cls.question_1 = questions[0]
        cls.question_2 = questions[1]
        cls.question_3 = questions[2]

    def create_exam(
        self,
        *,
        owner=None,
        title="Exam Engine Test",
        max_attempts=2,
        status=Exam.Status.DRAFT,
        starts_at=None,
        ends_at=None,
    ):
        return Exam.objects.create(
            owner=owner or self.teacher,
            title=title,
            duration_minutes=60,
            max_attempts=max_attempts,
            status=status,
            starts_at=starts_at,
            ends_at=ends_at,
        )

    def create_exam_question(
        self,
        *,
        exam,
        question=None,
        order=1,
        points=Decimal("1.00"),
    ):
        return ExamQuestion.objects.create(
            exam=exam,
            question=question or self.question_1,
            order=order,
            points=points,
            question_version=1,
        )

    # =========================================================
    # Exam validation
    # =========================================================

    def test_teacher_can_own_exam(self):
        exam = Exam(
            owner=self.teacher,
            title="Teacher Exam",
        )

        exam.full_clean()

    def test_student_cannot_own_exam(self):
        exam = Exam(
            owner=self.student,
            title="Invalid Owner",
        )

        with self.assertRaises(ValidationError):
            exam.full_clean()

    def test_unassigned_user_cannot_own_exam(self):
        exam = Exam(
            owner=self.unassigned_user,
            title="Invalid Owner",
        )

        with self.assertRaises(ValidationError):
            exam.full_clean()

    def test_exam_end_must_be_after_start(self):
        start = timezone.now()

        exam = Exam(
            owner=self.teacher,
            title="Invalid Schedule",
            starts_at=start,
            ends_at=start - timedelta(minutes=1),
        )

        with self.assertRaises(ValidationError):
            exam.full_clean()

    def test_published_exam_is_available_inside_window(self):
        now = timezone.now()

        exam = Exam(
            owner=self.teacher,
            title="Available Exam",
            status=Exam.Status.PUBLISHED,
            starts_at=now - timedelta(minutes=10),
            ends_at=now + timedelta(minutes=10),
        )

        exam.full_clean()

        self.assertTrue(
            exam.is_available_at(now)
        )

    def test_draft_exam_is_not_available(self):
        exam = Exam(
            owner=self.teacher,
            title="Draft Exam",
            status=Exam.Status.DRAFT,
        )

        self.assertFalse(
            exam.is_available_at()
        )

    # =========================================================
    # ExamQuestion constraints
    # =========================================================

    def test_same_question_cannot_be_added_twice(self):
        exam = self.create_exam()

        self.create_exam_question(
            exam=exam,
            question=self.question_1,
            order=1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_exam_question(
                    exam=exam,
                    question=self.question_1,
                    order=2,
                )

    def test_exam_question_order_must_be_unique(self):
        exam = self.create_exam()

        self.create_exam_question(
            exam=exam,
            question=self.question_1,
            order=1,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.create_exam_question(
                    exam=exam,
                    question=self.question_2,
                    order=1,
                )

    # =========================================================
    # ExamAttempt validation
    # =========================================================

    def test_student_can_own_attempt(self):
        exam = self.create_exam()

        attempt = ExamAttempt(
            exam=exam,
            student=self.student,
            attempt_number=1,
        )

        attempt.full_clean()

    def test_teacher_cannot_be_attempt_student(self):
        exam = self.create_exam()

        attempt = ExamAttempt(
            exam=exam,
            student=self.teacher,
            attempt_number=1,
        )

        with self.assertRaises(ValidationError):
            attempt.full_clean()

    def test_attempt_number_cannot_exceed_exam_limit(self):
        exam = self.create_exam(
            max_attempts=1,
        )

        attempt = ExamAttempt(
            exam=exam,
            student=self.student,
            attempt_number=2,
        )

        with self.assertRaises(ValidationError):
            attempt.full_clean()

    def test_attempt_deadline_must_be_after_start(self):
        exam = self.create_exam()

        start = timezone.now()

        attempt = ExamAttempt(
            exam=exam,
            student=self.student,
            attempt_number=1,
            started_at=start,
            deadline_at=start - timedelta(seconds=1),
        )

        with self.assertRaises(ValidationError):
            attempt.full_clean()

    def test_attempt_number_is_unique_per_exam_student(self):
        exam = self.create_exam(
            max_attempts=2,
        )

        ExamAttempt.objects.create(
            exam=exam,
            student=self.student,
            attempt_number=1,
            status=ExamAttempt.Status.SUBMITTED,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExamAttempt.objects.create(
                    exam=exam,
                    student=self.student,
                    attempt_number=1,
                    status=ExamAttempt.Status.SUBMITTED,
                )

    def test_only_one_active_attempt_per_exam_student(self):
        exam = self.create_exam(
            max_attempts=2,
        )

        ExamAttempt.objects.create(
            exam=exam,
            student=self.student,
            attempt_number=1,
            status=ExamAttempt.Status.IN_PROGRESS,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                ExamAttempt.objects.create(
                    exam=exam,
                    student=self.student,
                    attempt_number=2,
                    status=ExamAttempt.Status.IN_PROGRESS,
                )

    # =========================================================
    # StudentAnswer validation
    # =========================================================

    def test_answer_question_must_belong_to_attempt_exam(self):
        exam_1 = self.create_exam(
            title="Exam One",
        )

        exam_2 = self.create_exam(
            title="Exam Two",
        )

        exam_question_1 = self.create_exam_question(
            exam=exam_1,
            question=self.question_1,
            order=1,
        )

        exam_question_2 = self.create_exam_question(
            exam=exam_2,
            question=self.question_2,
            order=1,
        )

        attempt = ExamAttempt.objects.create(
            exam=exam_1,
            student=self.student,
            attempt_number=1,
        )

        answer = StudentAnswer(
            attempt=attempt,
            exam_question=exam_question_2,
            selected_answer=StudentAnswer.AnswerChoice.A,
        )

        with self.assertRaises(ValidationError):
            answer.full_clean()

        # Keep reference used so the first relation is also
        # guaranteed to have been created correctly.
        self.assertEqual(
            exam_question_1.exam_id,
            exam_1.id,
        )

    def test_only_one_answer_per_attempt_question(self):
        exam = self.create_exam()

        exam_question = self.create_exam_question(
            exam=exam,
            question=self.question_1,
            order=1,
        )

        attempt = ExamAttempt.objects.create(
            exam=exam,
            student=self.student,
            attempt_number=1,
        )

        StudentAnswer.objects.create(
            attempt=attempt,
            exam_question=exam_question,
            selected_answer=StudentAnswer.AnswerChoice.A,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                StudentAnswer.objects.create(
                    attempt=attempt,
                    exam_question=exam_question,
                    selected_answer=StudentAnswer.AnswerChoice.B,
                )

    def test_awarded_points_cannot_exceed_question_points(self):
        exam = self.create_exam()

        exam_question = self.create_exam_question(
            exam=exam,
            question=self.question_1,
            order=1,
            points=Decimal("2.00"),
        )

        attempt = ExamAttempt.objects.create(
            exam=exam,
            student=self.student,
            attempt_number=1,
        )

        answer = StudentAnswer(
            attempt=attempt,
            exam_question=exam_question,
            selected_answer=StudentAnswer.AnswerChoice.A,
            awarded_points=Decimal("3.00"),
        )

        with self.assertRaises(ValidationError):
            answer.full_clean()

    # =========================================================
    # ExamEvent validation
    # =========================================================

    def test_event_question_must_belong_to_attempt_exam(self):
        exam_1 = self.create_exam(
            title="Event Exam One",
        )

        exam_2 = self.create_exam(
            title="Event Exam Two",
        )

        exam_question_2 = self.create_exam_question(
            exam=exam_2,
            question=self.question_2,
            order=1,
        )

        attempt = ExamAttempt.objects.create(
            exam=exam_1,
            student=self.student,
            attempt_number=1,
        )

        event = ExamEvent(
            attempt=attempt,
            exam_question=exam_question_2,
            event_type=ExamEvent.EventType.QUESTION_VIEWED,
        )

        with self.assertRaises(ValidationError):
            event.full_clean()

    def test_valid_research_event(self):
        exam = self.create_exam()

        exam_question = self.create_exam_question(
            exam=exam,
            question=self.question_1,
            order=1,
        )

        attempt = ExamAttempt.objects.create(
            exam=exam,
            student=self.student,
            attempt_number=1,
        )

        event = ExamEvent(
            attempt=attempt,
            exam_question=exam_question,
            event_type=ExamEvent.EventType.QUESTION_VIEWED,
            payload={
                "source": "exam_ui",
            },
        )

        event.full_clean()
        event.save()

        self.assertEqual(
            event.attempt,
            attempt,
        )

        self.assertEqual(
            event.exam_question,
            exam_question,
        )