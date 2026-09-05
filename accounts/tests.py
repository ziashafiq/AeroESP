from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import (
    EmailVerificationCode,
    StudentProfile,
    TeacherProfile,
)


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

class RegistrationEmailTests(TestCase):
    """
    Covers the sign-up path end to end: a code must be emailed, and it
    must only work for the account pending verification in this
    session.
    """

    REGISTRATION_DATA = {
        "first_name": "Ali",
        "last_name": "Tester",
        "email": "ali.tester@example.com",
        "role": "STUDENT",
        "password1": "AeroESP-Strong-2026",
        "password2": "AeroESP-Strong-2026",
    }

    def _register(self, **overrides):

        data = dict(self.REGISTRATION_DATA)
        data.update(overrides)

        return self.client.post(
            reverse("accounts:register"),
            data,
        )

    def test_registration_emails_a_verification_code(self):

        response = self._register()

        self.assertRedirects(
            response,
            reverse("accounts:verify_email"),
        )

        self.assertEqual(
            len(mail.outbox),
            1,
        )

        message = mail.outbox[0]

        self.assertEqual(
            message.to,
            ["ali.tester@example.com"],
        )

        code = (
            EmailVerificationCode.objects
            .get(user__email="ali.tester@example.com")
            .code
        )

        # The code the user receives must be the stored one.
        self.assertIn(
            code,
            message.body,
        )

    def test_correct_code_verifies_and_creates_profile(self):

        self._register()

        code = (
            EmailVerificationCode.objects
            .get(user__email="ali.tester@example.com")
            .code
        )

        response = self.client.post(
            reverse("accounts:verify_email"),
            {"code": code},
        )

        self.assertRedirects(
            response,
            reverse("accounts:role_redirect"),
            target_status_code=302,
        )

        user = get_user_model().objects.get(
            email="ali.tester@example.com"
        )

        self.assertTrue(user.email_verified)

        self.assertTrue(
            StudentProfile.objects.filter(
                user=user
            ).exists()
        )

        self.assertTrue(
            EmailVerificationCode.objects.get(
                user=user
            ).is_used
        )

    def test_code_is_rejected_without_a_pending_session(self):
        """
        Regression: verify_email used to accept any unused code from
        any user, which logged the visitor in as that code's owner.
        """

        self._register()

        code = (
            EmailVerificationCode.objects
            .get(user__email="ali.tester@example.com")
            .code
        )

        attacker = Client()

        response = attacker.post(
            reverse("accounts:verify_email"),
            {"code": code},
        )

        self.assertRedirects(
            response,
            reverse("accounts:register"),
        )

        self.assertNotIn(
            "_auth_user_id",
            attacker.session,
        )

        self.assertFalse(
            get_user_model().objects.get(
                email="ali.tester@example.com"
            ).email_verified
        )

    def test_duplicate_email_local_part_gets_a_unique_username(self):

        self._register(email="ali@first.example.com")

        self.client = Client()

        self._register(email="ali@second.example.com")

        usernames = set(
            get_user_model().objects
            .filter(email__startswith="ali@")
            .values_list("username", flat=True)
        )

        self.assertEqual(
            len(usernames),
            2,
        )

    def test_resend_issues_a_new_code_and_retires_the_old_one(self):

        self._register()

        first_code = (
            EmailVerificationCode.objects
            .get(user__email="ali.tester@example.com")
            .code
        )

        self.client.post(
            reverse("accounts:resend_verification_code")
        )

        self.assertEqual(
            len(mail.outbox),
            2,
        )

        codes = (
            EmailVerificationCode.objects
            .filter(user__email="ali.tester@example.com")
            .order_by("created_at")
        )

        self.assertEqual(codes.count(), 2)

        self.assertTrue(codes[0].is_used)

        self.assertFalse(codes[1].is_used)

        # The retired code must no longer work.
        response = self.client.post(
            reverse("accounts:verify_email"),
            {"code": first_code},
        )

        self.assertEqual(response.status_code, 200)

    def test_delivery_failure_is_logged_and_surfaced(self):
        """
        Regression: a failing send used to be swallowed silently, so a
        broken mail setup looked exactly like a successful sign-up.
        """

        with mock.patch(
            "accounts.utils.send_mail",
            side_effect=OSError("Connection timed out"),
        ):

            with self.assertLogs(
                "accounts.utils",
                level="ERROR",
            ) as captured:

                response = self._register()

        # The failure must reach the log, with the address and cause.
        logged = "\n".join(captured.output)

        self.assertIn("FAILED to send", logged)
        self.assertIn("ali.tester@example.com", logged)
        self.assertIn("Connection timed out", logged)

        # ... and the user must not be told the mail is on its way.
        page = self.client.get(response["Location"])
        text = page.content.decode()

        self.assertIn("could not send", text.lower())
        self.assertNotIn("We sent a verification code", text)

    def test_non_delivering_backend_is_reported(self):

        with self.settings(
            EMAIL_BACKEND=(
                "django.core.mail.backends.console.EmailBackend"
            )
        ):

            with self.assertLogs(
                "accounts.utils",
                level="ERROR",
            ) as captured:

                self._register()

        self.assertIn(
            "does not send real mail",
            "\n".join(captured.output),
        )


@override_settings(REQUIRE_EMAIL_VERIFICATION=False)
class VerificationDisabledTests(TestCase):
    """
    AEROESP_REQUIRE_EMAIL_VERIFICATION=0: sign-up completes at once,
    nothing is mailed, and the code machinery stays dormant.
    """

    DATA = {
        "first_name": "Sara",
        "last_name": "Tester",
        "email": "sara.disabled@example.com",
        "role": "STUDENT",
        "password1": "AeroESP-Strong-2026",
        "password2": "AeroESP-Strong-2026",
    }

    def test_registration_logs_the_user_straight_in(self):

        response = self.client.post(
            reverse("accounts:register"),
            self.DATA,
        )

        self.assertRedirects(
            response,
            reverse("accounts:role_redirect"),
            target_status_code=302,
        )

        user = get_user_model().objects.get(
            email="sara.disabled@example.com"
        )

        self.assertTrue(user.email_verified)

        self.assertTrue(
            StudentProfile.objects.filter(user=user).exists()
        )

        self.assertEqual(
            str(self.client.session["_auth_user_id"]),
            str(user.pk),
        )

    def test_no_email_and_no_code_are_produced(self):

        self.client.post(
            reverse("accounts:register"),
            self.DATA,
        )

        self.assertEqual(len(mail.outbox), 0)

        self.assertFalse(
            EmailVerificationCode.objects.exists()
        )

    def test_verify_page_is_not_reachable(self):

        response = self.client.get(
            reverse("accounts:verify_email")
        )

        self.assertRedirects(
            response,
            reverse("accounts:login"),
        )

    def test_teacher_role_still_gets_a_teacher_profile(self):

        data = dict(self.DATA)
        data["email"] = "teacher.disabled@example.com"
        data["role"] = "TEACHER"

        self.client.post(
            reverse("accounts:register"),
            data,
        )

        user = get_user_model().objects.get(
            email="teacher.disabled@example.com"
        )

        self.assertTrue(
            TeacherProfile.objects.filter(user=user).exists()
        )


class PasswordResetAvailabilityTests(TestCase):

    @override_settings(
        EMAIL_BACKEND=(
            "django.core.mail.backends.console.EmailBackend"
        )
    )
    def test_reset_explains_itself_when_mail_cannot_be_sent(self):
        """
        Regression: without a working backend this raised, or claimed
        an email had been sent that never was.
        """

        response = self.client.get(
            reverse("password_reset")
        )

        self.assertEqual(response.status_code, 503)

        self.assertIn(
            "temporarily unavailable",
            response.content.decode(),
        )

    def test_reset_works_normally_with_a_sending_backend(self):

        response = self.client.get(
            reverse("password_reset")
        )

        self.assertEqual(response.status_code, 200)

        self.assertNotIn(
            "temporarily unavailable",
            response.content.decode(),
        )
