from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase, SimpleTestCase
from django.urls import reverse

from accounts.models import (
    StudentProfile,
    TeacherProfile,
)

from learning.models import LearningCourse
from learning.views import _course_level_from_cefr


# =========================================================
# Teacher Access Tests
# =========================================================

class LearningTeacherAccessTests(TestCase):

    def setUp(self):
        self.User = get_user_model()

        self.superuser = self.User.objects.create_superuser(
            username="superuser_test",
            email="super@test.local",
            password="SuperPass123!"
        )

        self.student = self.User.objects.create_user(
            username="student_test2",
            email="student2@test.local",
            password="StudentPass123!"
        )
        StudentProfile.objects.create(
            user=self.student,
            student_id="ST002",
            university="Test University",
            department="Aerospace Engineering",
            primary_aerospace_field=StudentProfile.AerospaceField.FLIGHT_DYNAMICS_CONTROL,
        )

        self.approved_teacher = self.User.objects.create_user(
            username="approved_teacher",
            email="approved@test.local",
            password="TeacherPass123!"
        )
        TeacherProfile.objects.create(
            user=self.approved_teacher,
            university="Test University",
            department="Aerospace Engineering",
            academic_email="approved@test.local",
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
            approved_by=self.superuser,
        )

        self.pending_teacher = self.User.objects.create_user(
            username="pending_teacher2",
            email="pending2@test.local",
            password="PendingPass123!"
        )
        TeacherProfile.objects.create(
            user=self.pending_teacher,
            university="Test University",
            department="Aerospace Engineering",
            academic_email="pending2@test.local",
            approval_status=TeacherProfile.ApprovalStatus.PENDING,
        )

        # Setup groups (assumes setup_roles has been run)
        call_command("setup_roles", stdout=StringIO())

    def test_student_cannot_access_teacher_analytics(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("learning:teacher_learning_dashboard")
        )
        self.assertEqual(response.status_code, 403)

    def test_pending_teacher_cannot_access_teacher_analytics(self):
        self.client.force_login(self.pending_teacher)
        response = self.client.get(
            reverse("learning:teacher_learning_dashboard")
        )
        self.assertEqual(response.status_code, 403)

    def test_approved_teacher_can_access_teacher_analytics(self):
        self.client.force_login(self.approved_teacher)
        response = self.client.get(
            reverse("learning:teacher_learning_dashboard")
        )
        self.assertEqual(response.status_code, 200)

    def test_superuser_can_access_teacher_analytics(self):
        self.client.force_login(self.superuser)
        response = self.client.get(
            reverse("learning:teacher_learning_dashboard")
        )
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_access_ai_dashboard(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("intelligence:dashboard")
        )
        self.assertEqual(response.status_code, 403)


# =========================================================
# Placement Level Mapping Tests
# =========================================================

class PlacementLevelMappingTests(SimpleTestCase):

    def test_cefr_course_level_mapping(self):
        cases = {
            "A1": LearningCourse.Level.BEGINNER,
            "A2": LearningCourse.Level.ELEMENTARY,
            "B1": LearningCourse.Level.INTERMEDIATE,
            "B2": LearningCourse.Level.UPPER_INTERMEDIATE,
            "C1": LearningCourse.Level.ADVANCED,
            "C2": LearningCourse.Level.ADVANCED,
        }

        for cefr, expected in cases.items():
            with self.subTest(cefr=cefr):
                self.assertEqual(
                    _course_level_from_cefr(cefr),
                    expected,
                )

    def test_unknown_cefr_returns_blank(self):
        self.assertEqual(
            _course_level_from_cefr("UNKNOWN"),
            "",
        )