import os
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import TeacherProfile
from assessment.models import Question

from intelligence.models import (
    GeneratedQuestionDraft,
    LearnerInsightSnapshot,
)

from intelligence.services import (
    QuestionGenerationError,
    build_learner_insight,
    get_question_generator,
)


User = get_user_model()


class IntelligenceProviderTests(
    TestCase
):

    def test_baseline_provider_loads(
        self,
    ):

        generator = (
            get_question_generator(
                "BASELINE_V1"
            )
        )

        self.assertEqual(
            generator.provider_name,
            "BASELINE_V1",
        )

    def test_openai_provider_loads(
        self,
    ):

        generator = (
            get_question_generator(
                "OPENAI_RESPONSES_V1"
            )
        )

        self.assertEqual(
            generator.provider_name,
            "OPENAI_RESPONSES_V1",
        )

    def test_openai_without_api_key_fails_safely(
        self,
    ):

        generator = (
            get_question_generator(
                "OPENAI_RESPONSES_V1"
            )
        )

        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "",
            },
        ):

            with self.assertRaises(
                QuestionGenerationError
            ):

                generator.generate(
                    track=(
                        Question.Track
                        .GENERAL_ENGLISH
                    ),
                    skill=(
                        Question.Skill
                        .VOCABULARY
                    ),
                    difficulty=(
                        Question.Difficulty
                        .BASIC
                    ),
                    theme=(
                        "Academic vocabulary"
                    ),
                )


class IntelligenceWorkflowTests(
    TestCase
):

    def setUp(
        self,
    ):

        self.teacher = (
            User.objects.create_user(
                username="ai_teacher",
                password="test-pass-123",
            )
        )

        TeacherProfile.objects.create(
            user=self.teacher,
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .APPROVED
            ),
        )

        self.other_teacher = (
            User.objects.create_user(
                username="other_teacher",
                password="test-pass-123",
            )
        )

        TeacherProfile.objects.create(
            user=self.other_teacher,
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .APPROVED
            ),
        )

        self.student = (
            User.objects.create_user(
                username="ai_student",
                password="test-pass-123",
            )
        )

    def test_non_teacher_cannot_access_ai_generator(
        self,
    ):

        self.client.force_login(
            self.student
        )

        response = self.client.get(
            reverse(
                "intelligence:"
                "generate_question"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    def test_baseline_generation_creates_pending_draft(
        self,
    ):

        self.client.force_login(
            self.teacher
        )

        response = self.client.post(
            reverse(
                "intelligence:"
                "generate_question"
            ),
            {
                "provider": (
                    "BASELINE_V1"
                ),
                "track": (
                    Question.Track
                    .GENERAL_ENGLISH
                ),
                "skill": (
                    Question.Skill
                    .VOCABULARY
                ),
                "difficulty": (
                    Question.Difficulty
                    .BASIC
                ),
                "domain": "",
                "topic": "",
                "theme": (
                    "Academic vocabulary"
                ),
                "teacher_instructions": (
                    "Create a clear "
                    "foundation-level item."
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            GeneratedQuestionDraft
            .objects
            .count(),
            1,
        )

        draft = (
            GeneratedQuestionDraft
            .objects
            .get()
        )

        self.assertEqual(
            draft.created_by,
            self.teacher,
        )

        self.assertEqual(
            draft.provider,
            "BASELINE_V1",
        )

        self.assertEqual(
            draft.status,
            GeneratedQuestionDraft
            .Status
            .PENDING,
        )

    def test_accept_draft_creates_ai_question(
        self,
    ):

        draft = (
            GeneratedQuestionDraft
            .objects
            .create(
                created_by=(
                    self.teacher
                ),
                track=(
                    Question.Track
                    .GENERAL_ENGLISH
                ),
                skill=(
                    Question.Skill
                    .VOCABULARY
                ),
                difficulty=(
                    Question.Difficulty
                    .BASIC
                ),
                theme="Vocabulary",
                question_text=(
                    "Which option best "
                    "matches the meaning "
                    "of 'rapid'?"
                ),
                option_a="Fast",
                option_b="Heavy",
                option_c="Quiet",
                option_d="Late",
                correct_answer="A",
                explanation=(
                    "Rapid means fast."
                ),
                provider=(
                    "BASELINE_V1"
                ),
            )
        )

        self.client.force_login(
            self.teacher
        )

        response = self.client.post(
            reverse(
                "intelligence:"
                "accept_generated_draft",
                kwargs={
                    "draft_id": (
                        draft.pk
                    ),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        draft.refresh_from_db()

        self.assertEqual(
            draft.status,
            GeneratedQuestionDraft
            .Status
            .ACCEPTED,
        )

        self.assertIsNotNone(
            draft.created_question_id
        )

        question = (
            draft.created_question
        )

        self.assertEqual(
            question.owner,
            self.teacher,
        )

        self.assertEqual(
            question.source_type,
            Question.SourceType.AI,
        )

        self.assertEqual(
            question.status,
            Question.Status.DRAFT,
        )

        self.assertEqual(
            question.visibility,
            Question.Visibility.PRIVATE,
        )

        self.assertEqual(
            question.track,
            Question.Track
            .GENERAL_ENGLISH,
        )

    def test_teacher_cannot_access_other_teachers_draft(
        self,
    ):

        draft = (
            GeneratedQuestionDraft
            .objects
            .create(
                created_by=(
                    self.teacher
                ),
                track=(
                    Question.Track
                    .GENERAL_ENGLISH
                ),
                skill=(
                    Question.Skill
                    .VOCABULARY
                ),
                difficulty=(
                    Question.Difficulty
                    .BASIC
                ),
                question_text=(
                    "Test question?"
                ),
                option_a="A1",
                option_b="B1",
                option_c="C1",
                option_d="D1",
                correct_answer="A",
            )
        )

        self.client.force_login(
            self.other_teacher
        )

        response = self.client.get(
            reverse(
                "intelligence:"
                "generated_draft_detail",
                kwargs={
                    "draft_id": (
                        draft.pk
                    ),
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_learner_insight_snapshot_is_created(
        self,
    ):

        snapshot = (
            build_learner_insight(
                self.student,
                "OVERALL",
            )
        )

        self.assertIsInstance(
            snapshot,
            LearnerInsightSnapshot,
        )

        self.assertEqual(
            snapshot.student,
            self.student,
        )

        self.assertEqual(
            snapshot.scope,
            "OVERALL",
        )

        self.assertGreaterEqual(
            snapshot.risk_score,
            0,
        )

        self.assertLessEqual(
            snapshot.risk_score,
            100,
        )

        self.assertTrue(
            snapshot.recommendations
        )