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


class AccountsFoundationTests(TestCase):

    def setUp(self):

        self.User = get_user_model()

        # =================================================
        # Admin
        # =================================================

        self.admin = self.User.objects.create_superuser(
            username="admin_test",
            email="admin@test.local",
            password="AdminPass123!",
        )

        # =================================================
        # Student
        # =================================================

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

        # =================================================
        # Approved Teacher
        # =================================================

        self.teacher = self.User.objects.create_user(
            username="teacher_test",
            email="teacher@test.local",
            password="TeacherPass123!",
        )

        TeacherProfile.objects.create(
            user=self.teacher,
            university="Test University",
            department="Aerospace Engineering",
            academic_email="teacher@test.local",
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .APPROVED
            ),
            approved_by=self.admin,
        )

        # =================================================
        # Pending Teacher
        # =================================================

        self.pending_teacher = (
            self.User.objects.create_user(
                username="pending_teacher",
                email="pending@test.local",
                password="PendingPass123!",
            )
        )

        TeacherProfile.objects.create(
            user=self.pending_teacher,
            university="Test University",
            department="Aerospace Engineering",
            academic_email="pending@test.local",
            approval_status=(
                TeacherProfile
                .ApprovalStatus
                .PENDING
            ),
        )

        # =================================================
        # Groups + Permissions
        # =================================================

        call_command(
            "setup_roles",
            stdout=StringIO(),
        )

    # =====================================================
    # Custom User
    # =====================================================

    def test_custom_user_model_is_active(self):

        self.assertEqual(
            self.User._meta.label,
            "accounts.CustomUser",
        )

    # =====================================================
    # Groups and Permissions
    # =====================================================

    def test_groups_and_question_permissions(self):

        self.assertTrue(
            self.student.groups.filter(
                name="Students"
            ).exists()
        )

        self.assertFalse(
            self.student.groups.filter(
                name="Teachers"
            ).exists()
        )

        self.assertTrue(
            self.teacher.groups.filter(
                name="Teachers"
            ).exists()
        )

        self.assertFalse(
            self.teacher.groups.filter(
                name="Students"
            ).exists()
        )

        # Teacher permissions
        self.assertTrue(
            self.teacher.has_perm(
                "assessment.view_question"
            )
        )

        self.assertTrue(
            self.teacher.has_perm(
                "assessment.add_question"
            )
        )

        self.assertTrue(
            self.teacher.has_perm(
                "assessment.change_question"
            )
        )

        self.assertFalse(
            self.teacher.has_perm(
                "assessment.delete_question"
            )
        )

        # Student permissions
        self.assertFalse(
            self.student.has_perm(
                "assessment.view_question"
            )
        )

        self.assertFalse(
            self.student.has_perm(
                "assessment.add_question"
            )
        )

        self.assertFalse(
            self.student.has_perm(
                "assessment.change_question"
            )
        )

    # =====================================================
    # Student Access
    # =====================================================

    def test_student_access_control(self):

        self.client.force_login(
            self.student
        )

        response = self.client.get(
            reverse(
                "accounts:student_dashboard"
            )
        )

        # Student dashboard now redirects to learning dashboard
        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            reverse(
                "learning:dashboard"
            ),
        )

        response = self.client.get(
            reverse(
                "accounts:teacher_dashboard"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # =====================================================
    # Approved Teacher Access
    # =====================================================

    def test_approved_teacher_access_control(self):

        self.client.force_login(
            self.teacher
        )

        response = self.client.get(
            reverse(
                "accounts:teacher_dashboard"
            )
        )

        # Teacher dashboard now redirects to learning:teacher_learning_dashboard
        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            response.url,
            reverse(
                "learning:teacher_learning_dashboard"
            ),
        )

        response = self.client.get(
            reverse(
                "accounts:student_dashboard"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # =====================================================
    # Pending Teacher
    # =====================================================

    def test_pending_teacher_cannot_access_dashboard(self):

        self.client.force_login(
            self.pending_teacher
        )

        response = self.client.get(
            reverse(
                "accounts:teacher_pending"
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        response = self.client.get(
            reverse(
                "accounts:teacher_dashboard"
            )
        )

        self.assertEqual(
            response.status_code,
            403,
        )

    # =====================================================
    # Universal Logout
    # =====================================================

    def test_universal_logout(self):

        self.client.force_login(
            self.admin
        )

        response = self.client.post(
            reverse(
                "accounts:logout"
            )
        )

        self.assertRedirects(
            response,
            reverse(
                "accounts:login"
            ),
        )

        response = self.client.get(
            reverse(
                "accounts:account_center"
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )


# =========================================================
# Teacher Access Tests (added after the Placement test)
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