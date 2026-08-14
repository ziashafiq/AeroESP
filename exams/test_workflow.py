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
from django.template.loader import (
    get_template,
)
from django.test import TestCase
from django.urls import reverse

from assessment.models import Question

from .models import (
    Exam,
    ExamQuestion,
)

from .views import (
    _publish_exam,
)


class ExamPublishWorkflowTests(
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

        cls.teachers_group = (
            Group.objects.get(
                name="Teachers"
            )
        )

        cls.teacher = (
            cls.User.objects
            .create_user(
                username=(
                    "workflow_teacher"
                ),
                email=(
                    "workflow_teacher"
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

        cls.teacher_2 = (
            cls.User.objects
            .create_user(
                username=(
                    "workflow_teacher_2"
                ),
                email=(
                    "workflow_teacher_2"
                    "@test.local"
                ),
                password=(
                    "TeacherPass123!"
                ),
            )
        )

        cls.teacher_2.groups.add(
            cls.teachers_group
        )

        questions = list(
            Question.objects
            .order_by("pk")[:4]
        )

        if len(questions) < 4:
            raise RuntimeError(
                "Workflow tests require "
                "at least four questions."
            )

        cls.question_1 = questions[0]
        cls.question_2 = questions[1]
        cls.question_3 = questions[2]
        cls.question_4 = questions[3]

        cls.question_1.owner = (
            cls.teacher
        )

        cls.question_1.save(
            update_fields=[
                "owner",
            ]
        )

        cls.question_2.owner = (
            cls.teacher
        )

        cls.question_2.save(
            update_fields=[
                "owner",
            ]
        )

    def create_exam(
        self,
        *,
        title="Workflow Exam",
    ):

        return Exam.objects.create(
            owner=self.teacher,
            title=title,
            duration_minutes=60,
            max_attempts=1,
        )

    def add_question(
        self,
        exam,
        question,
        order=1,
    ):

        return ExamQuestion.objects.create(
            exam=exam,
            question=question,
            order=order,
            question_version=(
                getattr(
                    question,
                    "version",
                    1,
                )
                or 1
            ),
        )

    def test_publish_requires_question(
        self,
    ):

        exam = self.create_exam()

        with self.assertRaises(
            ValidationError
        ):
            _publish_exam(
                exam
            )

    def test_publish_freezes_snapshot(
        self,
    ):

        exam = self.create_exam()

        link = self.add_question(
            exam,
            self.question_1,
        )

        published = _publish_exam(
            exam
        )

        published.refresh_from_db()
        link.refresh_from_db()

        self.assertEqual(
            published.status,
            Exam.Status.PUBLISHED,
        )

        self.assertIsNotNone(
            published.published_at
        )

        self.assertTrue(
            published.access_code
        )

        self.assertTrue(
            link.snapshot
        )

        self.assertEqual(
            link.snapshot[
                "question_id"
            ],
            self.question_1.pk,
        )

        self.assertIn(
            "question_text",
            link.snapshot[
                "fields"
            ],
        )

    def test_snapshot_survives_later_question_edit(
        self,
    ):

        original_text = (
            self.question_1
            .question_text
        )

        exam = self.create_exam()

        link = self.add_question(
            exam,
            self.question_1,
        )

        _publish_exam(
            exam
        )

        link.refresh_from_db()

        frozen_text = (
            link.snapshot[
                "fields"
            ][
                "question_text"
            ]
        )

        self.question_1.question_text = (
            "Changed after publication"
        )

        self.question_1.save(
            update_fields=[
                "question_text",
            ]
        )

        link.refresh_from_db()

        self.assertEqual(
            frozen_text,
            original_text,
        )

        self.assertEqual(
            link.snapshot[
                "fields"
            ][
                "question_text"
            ],
            original_text,
        )

    def test_second_publish_is_rejected(
        self,
    ):

        exam = self.create_exam()

        self.add_question(
            exam,
            self.question_1,
        )

        published = _publish_exam(
            exam
        )

        with self.assertRaises(
            ValidationError
        ):
            _publish_exam(
                published
            )

    def test_access_codes_are_unique(
        self,
    ):

        exam_1 = self.create_exam(
            title="Exam One",
        )

        exam_2 = self.create_exam(
            title="Exam Two",
        )

        self.add_question(
            exam_1,
            self.question_1,
        )

        self.add_question(
            exam_2,
            self.question_2,
        )

        exam_1 = _publish_exam(
            exam_1
        )

        exam_2 = _publish_exam(
            exam_2
        )

        self.assertNotEqual(
            exam_1.access_code,
            exam_2.access_code,
        )

    def test_other_teacher_question_is_rejected(
        self,
    ):

        source_field = (
            Question._meta
            .get_field(
                "source_type"
            )
        )

        non_seed_value = None

        for (
            value,
            label,
        ) in source_field.choices:

            if value != "SEED":
                non_seed_value = (
                    value
                )
                break

        if non_seed_value is None:
            self.skipTest(
                "No non-SEED source type "
                "exists."
            )

        self.question_3.owner = (
            self.teacher_2
        )

        self.question_3.source_type = (
            non_seed_value
        )

        self.question_3.save(
            update_fields=[
                "owner",
                "source_type",
            ]
        )

        exam = self.create_exam()

        self.add_question(
            exam,
            self.question_3,
        )

        with self.assertRaises(
            ValidationError
        ):
            _publish_exam(
                exam
            )

    def test_builder_urls_reverse(
        self,
    ):

        exam = self.create_exam()

        names = [
            (
                "exams:"
                "teacher_exam_list",
                {},
            ),
            (
                "exams:"
                "teacher_exam_create",
                {},
            ),
            (
                "exams:"
                "teacher_exam_detail",
                {
                    "pk": exam.pk,
                },
            ),
            (
                "exams:"
                "teacher_exam_edit",
                {
                    "pk": exam.pk,
                },
            ),
            (
                "exams:"
                "teacher_exam_question_bank",
                {
                    "pk": exam.pk,
                },
            ),
            (
                "exams:"
                "teacher_exam_structure",
                {
                    "pk": exam.pk,
                },
            ),
            (
                "exams:"
                "teacher_exam_publish",
                {
                    "pk": exam.pk,
                },
            ),
        ]

        for name, kwargs in names:

            url = reverse(
                name,
                kwargs=kwargs,
            )

            self.assertTrue(
                url
            )

    def test_builder_templates_load(
        self,
    ):

        template_names = [
            (
                "exams/teacher/"
                "base.html"
            ),
            (
                "exams/teacher/"
                "exam_list.html"
            ),
            (
                "exams/teacher/"
                "exam_form.html"
            ),
            (
                "exams/teacher/"
                "exam_detail.html"
            ),
            (
                "exams/teacher/"
                "question_bank.html"
            ),
            (
                "exams/teacher/"
                "exam_structure.html"
            ),
            (
                "exams/teacher/"
                "exam_publish.html"
            ),
        ]

        for template_name in (
            template_names
        ):

            template = get_template(
                template_name
            )

            self.assertIsNotNone(
                template
            )