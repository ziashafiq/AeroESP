from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import (
    Client,
    SimpleTestCase,
    TestCase,
    override_settings,
)
from django.utils import timezone
from django.urls import reverse

from .captcha import (
    ALPHABET,
    create_challenge,
    hash_answer,
    render_image,
    verify,
)
PNG_MAGIC = bytes.fromhex("89504E47")


from .models import (
    CaptchaChallenge,
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
        # CAPTCHA_TEST_MODE accepts this literal response.
        "captcha_0": "test-hashkey",
        "captcha_1": "PASSED",
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
        # CAPTCHA_TEST_MODE accepts this literal response.
        "captcha_0": "test-hashkey",
        "captcha_1": "PASSED",
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


class RegistrationCaptchaTests(TestCase):
    """
    The captcha is what stands between the sign-up form and automated
    registration, especially while email verification is switched off.
    """

    BASE = {
        "first_name": "Bot",
        "last_name": "Tester",
        "email": "bot.tester@example.com",
        "role": "STUDENT",
        "password1": "AeroESP-Strong-2026",
        "password2": "AeroESP-Strong-2026",
    }

    def _registered(self):
        return get_user_model().objects.filter(
            email="bot.tester@example.com"
        ).exists()

    def test_registration_without_a_captcha_is_rejected(self):

        response = self.client.post(
            reverse("accounts:register"),
            self.BASE,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._registered())

    def test_registration_with_a_wrong_answer_is_rejected(self):

        challenge = create_challenge()

        data = dict(self.BASE)
        data["captcha_0"] = challenge.key
        data["captcha_1"] = "WRONG"

        response = self.client.post(
            reverse("accounts:register"),
            data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._registered())

    def test_the_form_renders_a_locally_served_image(self):

        response = self.client.get(
            reverse("accounts:register")
        )

        content = response.content.decode()

        self.assertIn('name="captcha_0"', content)
        self.assertIn('name="captcha_1"', content)
        self.assertIn("/captcha/image/", content)

        # Nothing may be pulled from another host.
        self.assertNotIn("https://www.google.com", content)
        self.assertNotIn("hcaptcha", content)

    def test_image_endpoint_returns_a_png(self):

        challenge = create_challenge()

        response = self.client.get(
            reverse(
                "captcha_image",
                kwargs={"key": challenge.key},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertTrue(
            response.content.startswith(PNG_MAGIC)
        )

    def test_image_endpoint_404s_on_an_unknown_key(self):

        response = self.client.get(
            reverse(
                "captcha_image",
                kwargs={"key": "0" * 40},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_refresh_endpoint_issues_a_new_challenge(self):

        response = self.client.get(
            reverse("captcha_refresh")
        )

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertIn("key", payload)
        self.assertIn("/captcha/image/", payload["image_url"])

        self.assertTrue(
            CaptchaChallenge.objects.filter(
                key=payload["key"]
            ).exists()
        )


class CaptchaMechanicsTests(SimpleTestCase):

    def test_answers_are_not_stored_in_plain_text(self):

        answer = "ABCDE"

        self.assertNotIn(
            answer,
            hash_answer(answer),
        )

        self.assertEqual(
            hash_answer("abcde"),
            hash_answer("  ABCDE "),
            "comparison should ignore case and stray spaces",
        )

    def test_the_alphabet_omits_ambiguous_glyphs(self):

        for character in "O0I1L":
            self.assertNotIn(character, ALPHABET)

    def test_rendered_image_is_a_png(self):

        data = render_image("ABCDE")

        self.assertTrue(data.startswith(PNG_MAGIC))
        self.assertGreater(len(data), 500)


class CaptchaVerificationTests(TestCase):

    def test_a_correct_answer_passes_exactly_once(self):

        # create_challenge does not hand back the answer, so drive the
        # stored hash directly - this is what verify() compares against.
        challenge = create_challenge()
        challenge.answer_hash = hash_answer("ZZZZZ")
        challenge.save(update_fields=["answer_hash"])

        self.assertTrue(verify(challenge.key, "zzzzz"))

        # Consumed: the same key cannot be replayed.
        self.assertFalse(verify(challenge.key, "ZZZZZ"))

    def test_a_wrong_answer_also_consumes_the_challenge(self):
        """
        Otherwise one image could be guessed against repeatedly.
        """

        challenge = create_challenge()
        challenge.answer_hash = hash_answer("ZZZZZ")
        challenge.save(update_fields=["answer_hash"])

        self.assertFalse(verify(challenge.key, "WRONG"))
        self.assertFalse(verify(challenge.key, "ZZZZZ"))

    def test_an_expired_challenge_is_refused(self):

        challenge = create_challenge()
        challenge.answer_hash = hash_answer("ZZZZZ")
        challenge.expires_at = timezone.now() - timedelta(seconds=1)
        challenge.save()

        self.assertFalse(verify(challenge.key, "ZZZZZ"))

    def test_expired_rows_are_swept_when_issuing(self):

        stale = create_challenge()
        stale.expires_at = timezone.now() - timedelta(hours=1)
        stale.save(update_fields=["expires_at"])

        create_challenge()

        self.assertFalse(
            CaptchaChallenge.objects.filter(
                pk=stale.pk
            ).exists()
        )


class PasswordResetDeliveryTests(TestCase):
    """
    Django's PasswordResetForm swallows send failures and only logs
    them, so a broken mail service used to redirect the visitor to
    "check your email" for a message that was never sent.
    """

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            username="resetuser",
            email="reset.user@example.com",
            password="AeroESP-Strong-2026",
        )

    def _post(self, email):
        return self.client.post(
            reverse("password_reset"),
            {"email": email},
        )

    def test_a_failed_send_shows_the_support_page(self):

        with mock.patch(
            "django.core.mail.EmailMultiAlternatives.send",
            side_effect=OSError("Connection timed out"),
        ):

            with self.assertLogs("accounts.views", level="ERROR"):
                response = self._post("reset.user@example.com")

        self.assertEqual(response.status_code, 503)

        self.assertIn(
            "temporarily unavailable",
            response.content.decode(),
        )

    def test_a_working_send_reaches_the_done_page(self):

        response = self._post("reset.user@example.com")

        self.assertRedirects(
            response,
            reverse("password_reset_done"),
        )

        self.assertEqual(len(mail.outbox), 1)

    def test_an_unknown_address_is_not_disclosed(self):
        """
        Reporting success for an unregistered address is deliberate:
        the page must not reveal which emails have accounts.
        """

        response = self._post("nobody@example.com")

        self.assertRedirects(
            response,
            reverse("password_reset_done"),
        )

        self.assertEqual(len(mail.outbox), 0)


class ReviewerAccessSyncTests(TestCase):
    """
    Regression: approving a teacher never granted expert-reviewer
    access, so the "Expert Review" sidebar link never appeared and
    /expert-review/ stayed a 403 for everyone.
    """

    def setUp(self):

        self.teacher = get_user_model().objects.create_user(
            username="prof_reviewer",
            email="prof@example.com",
            password="AeroESP-Strong-2026",
        )

        self.profile = TeacherProfile.objects.create(
            user=self.teacher,
            university="Sharif University",
        )

    def test_approval_creates_an_active_reviewer_profile(self):

        from research_review.models import ExpertReviewerProfile

        self.assertFalse(
            ExpertReviewerProfile.objects.filter(
                user=self.teacher
            ).exists()
        )

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        reviewer = ExpertReviewerProfile.objects.get(
            user=self.teacher
        )

        self.assertTrue(reviewer.is_active_reviewer)
        self.assertEqual(
            reviewer.institution,
            "Sharif University",
        )

    def test_approval_does_not_overwrite_an_edited_profile(self):
        """
        An admin who changes discipline/institution by hand must not
        have that reset the next time the teacher record is saved.
        """

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        reviewer = ExpertReviewerProfile.objects.get(
            user=self.teacher
        )
        reviewer.discipline = "ESP"
        reviewer.institution = "Custom Institution"
        reviewer.save()

        # Re-saving the (still approved) teacher profile must not
        # clobber the admin's edits.
        self.profile.department = "Updated Department"
        self.profile.save()

        reviewer.refresh_from_db()

        self.assertEqual(reviewer.discipline, "ESP")
        self.assertEqual(reviewer.institution, "Custom Institution")

    def test_rejection_deactivates_an_existing_reviewer_profile(self):

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.REJECTED
        )
        self.profile.save()

        reviewer = ExpertReviewerProfile.objects.get(
            user=self.teacher
        )

        self.assertFalse(reviewer.is_active_reviewer)

    def test_pending_status_creates_no_reviewer_profile(self):

        from research_review.models import ExpertReviewerProfile

        self.assertFalse(
            ExpertReviewerProfile.objects.filter(
                user=self.teacher
            ).exists()
        )

    def test_approved_teacher_can_reach_the_review_dashboard(self):
        """
        End-to-end: the sidebar link and the view itself both gate on
        expert_reviewer_profile.is_active_reviewer.
        """

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self.client.force_login(self.teacher)

        response = self.client.get(
            reverse("research_review:dashboard")
        )

        self.assertEqual(response.status_code, 200)


class UsernameDisclosureTests(TestCase):
    """
    The username is generated from the email's local part and shown
    nowhere unless the flow surfaces it explicitly - a returning user
    who forgot it had no way to look it up.
    """

    def _messages(self, response):
        return [
            str(m)
            for m in response.wsgi_request._messages
        ]

    def test_immediate_registration_shows_the_username(self):

        with self.settings(REQUIRE_EMAIL_VERIFICATION=False):

            response = self.client.post(
                reverse("accounts:register"),
                {
                    "first_name": "Nora",
                    "last_name": "Tester",
                    "email": "nora.tester@example.com",
                    "role": "STUDENT",
                    "password1": "AeroESP-Strong-2026",
                    "password2": "AeroESP-Strong-2026",
                    "captcha_0": "x",
                    "captcha_1": "PASSED",
                },
                follow=True,
            )

        user = get_user_model().objects.get(
            email="nora.tester@example.com"
        )

        joined = " ".join(self._messages(response))

        self.assertIn(user.username, joined)

    def test_verification_success_shows_the_username(self):

        self.client.post(
            reverse("accounts:register"),
            {
                "first_name": "Omid",
                "last_name": "Tester",
                "email": "omid.tester@example.com",
                "role": "STUDENT",
                "password1": "AeroESP-Strong-2026",
                "password2": "AeroESP-Strong-2026",
                "captcha_0": "x",
                "captcha_1": "PASSED",
            },
        )

        user = get_user_model().objects.get(
            email="omid.tester@example.com"
        )

        code = EmailVerificationCode.objects.get(
            user=user
        ).code

        response = self.client.post(
            reverse("accounts:verify_email"),
            {"code": code},
            follow=True,
        )

        joined = " ".join(self._messages(response))

        self.assertIn(user.username, joined)

    def test_account_center_always_shows_the_username(self):

        user = get_user_model().objects.create_user(
            username="visibleuser",
            email="visible@example.com",
            password="AeroESP-Strong-2026",
        )

        StudentProfile.objects.create(user=user)

        self.client.force_login(user)

        response = self.client.get(
            reverse("accounts:account_center")
        )

        self.assertContains(response, "visibleuser")


@override_settings(AEROESP_INVITE_CODE="AERO-BETA-2026")
class InviteCodeTests(TestCase):
    """
    AEROESP_INVITE_CODE gates registration during the closed reviewer
    beta. Left unset (the default, covered elsewhere), the field must
    not exist at all.
    """

    DATA = {
        "first_name": "Cody",
        "last_name": "Tester",
        "email": "cody.tester@example.com",
        "role": "STUDENT",
        "password1": "AeroESP-Strong-2026",
        "password2": "AeroESP-Strong-2026",
        "captcha_0": "x",
        "captcha_1": "PASSED",
    }

    def _registered(self):
        return get_user_model().objects.filter(
            email="cody.tester@example.com"
        ).exists()

    def test_field_is_required_when_a_code_is_configured(self):

        response = self.client.post(
            reverse("accounts:register"),
            self.DATA,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._registered())

    def test_wrong_code_is_rejected(self):

        data = dict(self.DATA, invite_code="wrong-code")

        response = self.client.post(
            reverse("accounts:register"),
            data,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._registered())

    def test_correct_code_allows_registration(self):

        data = dict(
            self.DATA,
            invite_code="AERO-BETA-2026",
        )

        response = self.client.post(
            reverse("accounts:register"),
            data,
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(self._registered())

    def test_the_field_is_rendered_on_the_form(self):

        response = self.client.get(
            reverse("accounts:register")
        )

        self.assertContains(response, "invite_code")


class InviteCodeDisabledByDefaultTests(TestCase):
    """
    The default (no AEROESP_INVITE_CODE set) must not change existing
    sign-up behaviour at all.
    """

    def test_no_invite_field_when_unconfigured(self):

        response = self.client.get(
            reverse("accounts:register")
        )

        self.assertNotContains(response, "invite_code")

    def test_registration_succeeds_without_any_code(self):

        response = self.client.post(
            reverse("accounts:register"),
            {
                "first_name": "Dara",
                "last_name": "Tester",
                "email": "dara.tester@example.com",
                "role": "STUDENT",
                "password1": "AeroESP-Strong-2026",
                "password2": "AeroESP-Strong-2026",
                "captcha_0": "x",
                "captcha_1": "PASSED",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            get_user_model().objects.filter(
                email="dara.tester@example.com"
            ).exists()
        )
