from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from accounts.models import (
    StudentProfile,
    TeacherProfile,
)

from .forms import TeacherQuestionForm
from .models import (
    AerospaceDomain,
    AerospaceTopic,
    Question,
)


class AssessmentFoundationTests(TestCase):

    def setUp(self):

        self.User = get_user_model()

        # =================================================
        # Users
        # =================================================

        self.admin = self.User.objects.create_superuser(
            username="admin_test",
            email="admin@test.local",
            password="AdminPass123!",
        )

        self.teacher = self.User.objects.create_user(
            username="teacher_one",
            email="teacher1@test.local",
            password="TeacherPass123!",
        )

        TeacherProfile.objects.create(
            user=self.teacher,
            university="Test University",
            department="Aerospace Engineering",
            academic_email="teacher1@test.local",
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .APPROVED
            ),
            approved_by=self.admin,
        )

        self.teacher_two = (
            self.User.objects.create_user(
                username="teacher_two",
                email="teacher2@test.local",
                password="TeacherPass123!",
            )
        )

        TeacherProfile.objects.create(
            user=self.teacher_two,
            university="Test University",
            department="Aerospace Engineering",
            academic_email="teacher2@test.local",
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .APPROVED
            ),
            approved_by=self.admin,
        )

        self.student = self.User.objects.create_user(
            username="student_test",
            email="student@test.local",
            password="StudentPass123!",
        )

        StudentProfile.objects.create(
            user=self.student,
            student_id="ST001",
            university="Test University",
            department="Aerospace Engineering",
            primary_aerospace_field=(
                StudentProfile
                .AerospaceField
                .FLIGHT_DYNAMICS_CONTROL
            ),
        )

        call_command(
            "setup_roles",
            stdout=StringIO(),
        )

        # =================================================
        # Domains
        # =================================================

        self.flight_domain = (
            AerospaceDomain.objects.create(
                code="FLIGHT",
                name=(
                    "Flight Mechanics, Dynamics & Control"
                ),
                order=1,
            )
        )

        self.aero_domain = (
            AerospaceDomain.objects.create(
                code="AERO",
                name="Aerodynamics & Fluid Mechanics",
                order=2,
            )
        )

        # =================================================
        # Valid Topics
        # =================================================

        self.flight_control = (
            AerospaceTopic.objects.create(
                domain=self.flight_domain,
                code="FLIGHT_CONTROL",
                name="Flight Control",
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .CORE
                ),
                is_active=True,
                order=1,
            )
        )

        self.guidance = (
            AerospaceTopic.objects.create(
                domain=self.flight_domain,
                code="GUIDANCE",
                name="Guidance",
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .APPROVED
                ),
                is_active=True,
                order=2,
            )
        )

        self.aero_control_surface = (
            AerospaceTopic.objects.create(
                domain=self.aero_domain,
                code="CONTROL_SURFACE",
                name="Aerodynamic Control Surface",
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .CORE
                ),
                is_active=True,
                order=1,
            )
        )

        # Topic that must NOT appear in teacher searches.
        self.pending_control = (
            AerospaceTopic.objects.create(
                domain=self.flight_domain,
                code="PENDING_CONTROL",
                name="Pending Control Topic",
                approval_status=(
                    AerospaceTopic
                    .ApprovalStatus
                    .PENDING
                ),
                is_active=False,
                order=999,
                created_by=self.teacher,
            )
        )

    # =====================================================
    # Question Factory
    # =====================================================

    def create_question(
        self,
        owner=None,
        domain=None,
        topic=None,
        text="Test aerospace question?",
    ):

        domain = (
            domain
            or self.flight_domain
        )

        topic = (
            topic
            or self.flight_control
        )

        return Question.objects.create(
            owner=owner,
            question_text=text,
            option_a="Option A",
            option_b="Option B",
            option_c="Option C",
            option_d="Option D",
            correct_answer="A",
            explanation="Test explanation",
            question_language=(
                Question.Language.ENGLISH
            ),
            options_language=(
                Question.Language.ENGLISH
            ),
            skill=(
                Question.Skill.VOCABULARY
            ),
            aerospace_domain=domain.code,
            topic=topic.name,
            difficulty=(
                Question.Difficulty.BASIC
            ),
            domain_ref=domain,
            topic_ref=topic,
            source_type=(
                Question.SourceType.MANUAL
            ),
            status=(
                Question.Status.DRAFT
            ),
            visibility=(
                Question.Visibility.PRIVATE
            ),
        )

    # =====================================================
    # Topic Search
    # =====================================================

    def test_topic_search_is_domain_limited(self):

        self.client.force_login(
            self.teacher
        )

        response = self.client.get(
            reverse(
                "teacher_questions:topic_search"
            ),
            {
                "domain":
                    self.flight_domain.id,
                "q":
                    "control",
            },
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        names = {
            item["name"]
            for item in data["results"]
        }

        # Same domain + approved/core
        self.assertIn(
            "Flight Control",
            names,
        )

        # Wrong domain must not appear
        self.assertNotIn(
            "Aerodynamic Control Surface",
            names,
        )

        # Pending topic must not appear
        self.assertNotIn(
            "Pending Control Topic",
            names,
        )

    # =====================================================
    # Owner must not be editable from Teacher Form
    # =====================================================

    def test_teacher_form_does_not_expose_owner(self):

        form = TeacherQuestionForm()

        self.assertNotIn(
            "owner",
            form.fields,
        )

    # =====================================================
    # Question Creation
    # =====================================================

    def test_question_creation_assigns_teacher_owner(self):

        self.client.force_login(
            self.teacher
        )

        response = self.client.post(
            reverse(
                "teacher_questions:create"
            ),
            {
                "question_text":
                    "What is static stability?",

                "option_a":
                    "Initial tendency after disturbance",

                "option_b":
                    "Fuel efficiency",

                "option_c":
                    "Engine thrust",

                "option_d":
                    "Wing fatigue",

                "correct_answer":
                    "A",

                "explanation":
                    "Static stability describes "
                    "the initial tendency.",

                "question_language":
                    Question.Language.ENGLISH,

                "options_language":
                    Question.Language.ENGLISH,

                "skill":
                    Question.Skill.VOCABULARY,

                "domain_ref":
                    self.flight_domain.id,

                "topic_ref":
                    self.flight_control.id,

                "difficulty":
                    Question.Difficulty.BASIC,

                "source_reference":
                    "Test source",

                "visibility":
                    Question.Visibility.PRIVATE,
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        question = Question.objects.get(
            question_text=(
                "What is static stability?"
            )
        )

        self.assertEqual(
            question.owner,
            self.teacher,
        )

        self.assertEqual(
            question.status,
            Question.Status.DRAFT,
        )

        self.assertEqual(
            question.source_type,
            Question.SourceType.MANUAL,
        )

        self.assertEqual(
            question.aerospace_domain,
            "FLIGHT",
        )

        self.assertEqual(
            question.topic,
            "Flight Control",
        )

    # =====================================================
    # Object Ownership Security
    # =====================================================

    def test_teacher_cannot_edit_another_teacher_question(
        self
    ):

        question = self.create_question(
            owner=self.teacher_two
        )

        self.client.force_login(
            self.teacher
        )

        response = self.client.get(
            reverse(
                "teacher_questions:edit",
                args=[
                    question.id
                ],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # =====================================================
    # Student Security
    # =====================================================

    def test_student_cannot_access_teacher_question_bank(
        self
    ):

        self.client.force_login(
            self.student
        )

        response = self.client.get(
            reverse(
                "teacher_questions:list"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

        response = self.client.get(
            reverse(
                "teacher_questions:create"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # =====================================================
    # Topic Proposal Workflow
    # =====================================================

    def test_topic_proposal_is_created_pending_and_inactive(
        self
    ):

        self.client.force_login(
            self.teacher
        )

        response = self.client.post(
            reverse(
                "teacher_questions:topic_propose"
            ),
            {
                "domain":
                    self.flight_domain.id,

                "parent":
                    self.flight_control.id,

                "name":
                    "Fault-Tolerant Flight Control",

                "description":
                    "Control after actuator or sensor failure.",
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        proposal = (
            AerospaceTopic.objects.get(
                name="Fault-Tolerant Flight Control"
            )
        )

        self.assertEqual(
            proposal.created_by,
            self.teacher,
        )

        self.assertEqual(
            proposal.approval_status,
            AerospaceTopic
            .ApprovalStatus
            .PENDING,
        )

        self.assertFalse(
            proposal.is_active
        )

        self.assertEqual(
            proposal.parent,
            self.flight_control,
        )

    # =====================================================
    # Question Taxonomy Validation
    # =====================================================

    def test_question_rejects_topic_from_wrong_domain(
        self
    ):

        question = Question(
            question_text="Validation test?",
            option_a="A",
            option_b="B",
            option_c="C",
            option_d="D",
            correct_answer="A",
            skill=(
                Question.Skill.VOCABULARY
            ),
            aerospace_domain="FLIGHT",
            difficulty=(
                Question.Difficulty.BASIC
            ),
            domain_ref=self.flight_domain,
            topic_ref=(
                self.aero_control_surface
            ),
        )

        with self.assertRaises(
            ValidationError
        ):
            question.full_clean()

    # =====================================================
    # Rejection Reason
    # =====================================================

    def test_rejected_topic_requires_review_reason(
        self
    ):

        proposal = AerospaceTopic(
            domain=self.flight_domain,
            code="REJECT_TEST",
            name="Rejected Test Topic",
            approval_status=(
                AerospaceTopic
                .ApprovalStatus
                .REJECTED
            ),
            is_active=False,
            review_note="",
        )

        with self.assertRaises(
            ValidationError
        ):
            proposal.full_clean()

        proposal.review_note = (
            "Outside the current taxonomy scope."
        )

        # This should now pass.
        proposal.full_clean()

    # =====================================================
    # Parent Domain Validation
    # =====================================================

    def test_parent_topic_must_use_same_domain(
        self
    ):

        topic = AerospaceTopic(
            domain=self.aero_domain,
            parent=self.flight_control,
            code="BAD_PARENT",
            name="Bad Parent Topic",
        )

        with self.assertRaises(
            ValidationError
        ):
            topic.full_clean()


# =========================================================
# Bootstrap / Seed Command
# =========================================================

class BootstrapDemoCommandTests(TestCase):

    def test_bootstrap_command_is_idempotent(self):

        output = StringIO()

        call_command(
            "bootstrap_aeroesp_demo",
            stdout=output,
        )

        self.assertEqual(
            AerospaceDomain.objects.count(),
            12,
        )

        self.assertGreaterEqual(
            AerospaceTopic.objects.count(),
            100,
        )

        self.assertEqual(
            Question.objects.filter(
                source_reference__startswith=(
                    "DEMO100::"
                )
            ).count(),
            100,
        )

        # Run it again.
        # Counts must not duplicate.
        call_command(
            "bootstrap_aeroesp_demo",
            stdout=StringIO(),
        )

        self.assertEqual(
            AerospaceDomain.objects.count(),
            12,
        )

        self.assertEqual(
            Question.objects.filter(
                source_reference__startswith=(
                    "DEMO100::"
                )
            ).count(),
            100,
        )