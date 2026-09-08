from datetime import timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
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
    HelpGuide,
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
        "agree_terms": "on",
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
        "agree_terms": "on",
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
        "agree_terms": "on",
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
    Teacher approval and expert-reviewer status are two independent
    decisions. Approving a teacher must never, on its own, hand out
    reviewer access; that takes the deliberate
    "Promote to expert reviewer" admin action.
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

    def _promote(self):
        """Run the admin action the way the admin screen does."""

        from django.contrib.admin.sites import AdminSite
        from django.test import RequestFactory
        from django.contrib.messages.storage.fallback import (
            FallbackStorage,
        )

        from accounts.admin import TeacherProfileAdmin

        request = RequestFactory().post("/admin/")
        request.user = self.teacher
        request.session = {}
        request._messages = FallbackStorage(request)

        model_admin = TeacherProfileAdmin(
            TeacherProfile,
            AdminSite(),
        )
        model_admin.promote_to_expert_reviewer(
            request,
            TeacherProfile.objects.filter(pk=self.profile.pk),
        )

        return request

    def test_approval_alone_creates_no_reviewer_profile(self):
        """
        The whole point of the split: approving a teacher is not also
        a decision to let them grade research items.
        """

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self.assertFalse(
            ExpertReviewerProfile.objects.filter(
                user=self.teacher
            ).exists()
        )

    def test_repeated_saves_of_an_approved_teacher_create_nothing(self):

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self.profile.department = "Updated Department"
        self.profile.save()

        self.profile.university = "Another University"
        self.profile.save()

        self.assertEqual(
            ExpertReviewerProfile.objects.filter(
                user=self.teacher
            ).count(),
            0,
        )

    def test_promote_action_grants_reviewer_access(self):

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self._promote()

        reviewer = ExpertReviewerProfile.objects.get(
            user=self.teacher
        )

        self.assertTrue(reviewer.is_active_reviewer)
        self.assertEqual(reviewer.institution, "Sharif University")

    def test_promote_action_refuses_an_unapproved_teacher(self):
        """
        Independent decisions, but not contradictory ones: reviewing
        still presumes the teacher account itself stands.
        """

        from research_review.models import ExpertReviewerProfile

        self.assertEqual(
            self.profile.approval_status,
            TeacherProfile.ApprovalStatus.PENDING,
        )

        self._promote()

        self.assertFalse(
            ExpertReviewerProfile.objects.filter(
                user=self.teacher
            ).exists()
        )

    def test_promote_action_does_not_overwrite_an_edited_profile(self):
        """
        An admin who changes discipline/institution by hand must not
        have that reset by promoting again.
        """

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self._promote()

        reviewer = ExpertReviewerProfile.objects.get(
            user=self.teacher
        )
        reviewer.discipline = "ESP"
        reviewer.institution = "Custom Institution"
        reviewer.save()

        self._promote()

        reviewer.refresh_from_db()

        self.assertEqual(reviewer.discipline, "ESP")
        self.assertEqual(reviewer.institution, "Custom Institution")

    def test_promote_action_reactivates_a_revoked_reviewer(self):

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self._promote()

        ExpertReviewerProfile.objects.filter(
            user=self.teacher
        ).update(is_active_reviewer=False)

        self._promote()

        self.assertTrue(
            ExpertReviewerProfile.objects.get(
                user=self.teacher
            ).is_active_reviewer
        )

    def test_rejection_deactivates_an_existing_reviewer_profile(self):
        """
        The one direction still automatic. It can only remove access,
        never grant it, so it cannot hand out a privilege unasked.
        """

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self._promote()

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.REJECTED
        )
        self.profile.save()

        reviewer = ExpertReviewerProfile.objects.get(
            user=self.teacher
        )

        self.assertFalse(reviewer.is_active_reviewer)

    def test_re_approval_does_not_restore_reviewer_access(self):
        """
        Revocation is not undone by fixing the teacher record; getting
        the role back takes the explicit action again.
        """

        from research_review.models import ExpertReviewerProfile

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()
        self._promote()

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.REJECTED
        )
        self.profile.save()

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self.assertFalse(
            ExpertReviewerProfile.objects.get(
                user=self.teacher
            ).is_active_reviewer
        )

    def test_pending_status_creates_no_reviewer_profile(self):

        from research_review.models import ExpertReviewerProfile

        self.assertFalse(
            ExpertReviewerProfile.objects.filter(
                user=self.teacher
            ).exists()
        )

    def test_approved_teacher_cannot_reach_the_review_dashboard(self):
        """
        Approval alone no longer opens /expert-review/.
        """

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self.client.force_login(self.teacher)

        response = self.client.get(
            reverse("research_review:dashboard")
        )

        self.assertNotEqual(response.status_code, 200)

    def test_promoted_teacher_can_reach_the_review_dashboard(self):
        """
        End-to-end: the sidebar link and the view itself both gate on
        expert_reviewer_profile.is_active_reviewer.
        """

        self.profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.profile.save()

        self._promote()

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
                    "agree_terms": "on",
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
                "agree_terms": "on",
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
        "agree_terms": "on",
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
                "agree_terms": "on",
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


class TermsOfUseTests(TestCase):
    """
    Confidentiality of assessment content is a legal position the
    project needs to be able to point to, so acceptance must be
    required and timestamped, and the page itself must exist.
    """

    # Deliberately missing agree_terms: several tests below check what
    # happens without it.
    DATA = {
        "first_name": "Tara",
        "last_name": "Tester",
        "email": "tara.tester@example.com",
        "role": "STUDENT",
        "password1": "AeroESP-Strong-2026",
        "password2": "AeroESP-Strong-2026",
        "captcha_0": "x",
        "captcha_1": "PASSED",
    }

    def test_registration_without_accepting_terms_is_rejected(self):

        response = self.client.post(
            reverse("accounts:register"),
            self.DATA,
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            get_user_model().objects.filter(
                email="tara.tester@example.com"
            ).exists()
        )

    def test_accepting_terms_records_a_timestamp(self):

        before = timezone.now()

        response = self.client.post(
            reverse("accounts:register"),
            dict(self.DATA, agree_terms="on"),
        )

        self.assertEqual(response.status_code, 302)

        user = get_user_model().objects.get(
            email="tara.tester@example.com"
        )

        self.assertIsNotNone(user.terms_accepted_at)
        self.assertGreaterEqual(
            user.terms_accepted_at,
            before,
        )

    def test_terms_page_is_reachable(self):

        response = self.client.get(
            reverse("terms")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Confidentiality")

    def test_terms_link_appears_on_the_registration_form(self):

        response = self.client.get(
            reverse("accounts:register")
        )

        self.assertContains(response, 'href="/terms/"')

    def test_terms_link_appears_in_the_public_footer(self):

        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            reverse("terms"),
        )


class HelpGuideTests(TestCase):
    """
    Guides must be editable purely through the admin (no code touched
    to publish or correct one) and must reach the right audience.
    """

    def setUp(self):

        self.student_guide = HelpGuide.objects.create(
            audience=HelpGuide.Audience.STUDENT,
            slug="student-getting-started",
            title="Getting started as a Student",
            summary="How to begin learning on AeroESP.",
            body="Line one.\nLine two.",
        )

        self.reviewer_guide = HelpGuide.objects.create(
            audience=HelpGuide.Audience.EXPERT_REVIEWER,
            slug="expert-reviewer-getting-started",
            title="Reviewing AI-generated questions",
        )

        self.draft_guide = HelpGuide.objects.create(
            audience=HelpGuide.Audience.TEACHER,
            slug="unpublished-teacher-guide",
            title="Not ready yet",
            is_published=False,
        )

    def test_public_list_shows_only_published_guides(self):

        response = self.client.get(
            reverse("help_list")
        )

        self.assertContains(
            response,
            "Getting started as a Student",
        )
        self.assertNotContains(
            response,
            "Not ready yet",
        )

    def test_unpublished_guide_detail_is_not_reachable(self):

        response = self.client.get(
            reverse(
                "help_detail",
                args=["unpublished-teacher-guide"],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_published_guide_detail_renders_the_body(self):

        response = self.client.get(
            self.student_guide.get_absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Line one.")

    def test_landing_page_lists_published_guides(self):

        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            "Getting started as a Student",
        )

    def test_help_for_me_routes_a_student_to_the_student_audience(self):

        user = get_user_model().objects.create_user(
            username="helpstudent",
            email="helpstudent@example.com",
            password="AeroESP-Strong-2026",
        )
        StudentProfile.objects.create(user=user)

        self.client.force_login(user)

        response = self.client.get(
            reverse("help_for_me")
        )

        self.assertRedirects(
            response,
            f"{reverse('help_list')}?audience=STUDENT",
        )

    def test_help_for_me_prefers_reviewer_over_teacher(self):

        from research_review.models import ExpertReviewerProfile

        user = get_user_model().objects.create_user(
            username="helpreviewer",
            email="helpreviewer@example.com",
            password="AeroESP-Strong-2026",
        )

        TeacherProfile.objects.create(
            user=user,
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
        )

        # Created explicitly: teacher approval no longer implies
        # reviewer access.
        ExpertReviewerProfile.objects.create(
            user=user,
            discipline="AEROSPACE",
            is_active_reviewer=True,
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("help_for_me")
        )

        self.assertRedirects(
            response,
            f"{reverse('help_list')}?audience=EXPERT_REVIEWER",
        )

    def test_help_for_me_sends_a_logged_out_visitor_to_the_full_list(self):

        response = self.client.get(
            reverse("help_for_me")
        )

        self.assertRedirects(
            response,
            reverse("help_list"),
        )

    def test_topbar_help_icon_appears_for_signed_in_users(self):

        user = get_user_model().objects.create_user(
            username="helpicon",
            email="helpicon@example.com",
            password="AeroESP-Strong-2026",
        )
        StudentProfile.objects.create(user=user)

        self.client.force_login(user)

        response = self.client.get(
            reverse("accounts:account_center")
        )

        self.assertContains(
            response,
            reverse("help_for_me"),
        )


class ReviewerGettingStartedPageTests(TestCase):

    def test_falls_back_to_the_built_in_page_when_no_guide_exists(self):

        response = self.client.get(
            reverse("research_review:getting_started")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Create an account as a Teacher")

    def test_redirects_to_an_admin_written_guide_when_one_exists(self):

        HelpGuide.objects.create(
            audience=HelpGuide.Audience.EXPERT_REVIEWER,
            slug="expert-reviewer-getting-started",
            title="Custom Reviewer Guide",
            body="Written by the admin.",
        )

        response = self.client.get(
            reverse("research_review:getting_started")
        )

        self.assertRedirects(
            response,
            "/help/expert-reviewer-getting-started/",
        )

    def test_page_requires_no_login(self):
        """
        The whole point is to walk a prospective reviewer through
        registering, so it cannot be gated behind an account.
        """

        response = self.client.get(
            reverse("research_review:getting_started")
        )

        self.assertEqual(response.status_code, 200)


class SupportContactLinkTests(TestCase):
    """
    A support address configured anywhere reaches every page through
    accounts.context_processors.support_email, so reviewers always
    have a way to report a problem.
    """

    def test_public_footer_shows_a_report_link_when_configured(self):

        with self.settings(AEROESP_SUPPORT_EMAIL="help@example.com"):

            response = self.client.get(reverse("home"))

            self.assertContains(
                response,
                "mailto:help@example.com",
            )

    def test_signed_in_sidebar_shows_a_report_link_when_configured(self):

        user = get_user_model().objects.create_user(
            username="supportcheck",
            email="supportcheck@example.com",
            password="AeroESP-Strong-2026",
        )
        StudentProfile.objects.create(user=user)

        self.client.force_login(user)

        with self.settings(AEROESP_SUPPORT_EMAIL="help@example.com"):

            response = self.client.get(
                reverse("accounts:account_center")
            )

            self.assertContains(
                response,
                "mailto:help@example.com",
            )

    def test_no_broken_mailto_when_support_email_is_unset(self):

        with self.settings(AEROESP_SUPPORT_EMAIL=""):

            response = self.client.get(reverse("home"))

            self.assertNotContains(response, "mailto:")


class RolePermissionAutoSyncTests(TestCase):
    """
    Regression: a fresh deployment where nobody has ever run
    `manage.py setup_roles` by hand left the "Teachers" Django group
    with zero permissions, so an admin-approved teacher got 403 on
    /teacher/questions/ despite passing every application-level
    approval check.

    Deliberately does NOT call setup_roles anywhere in this test - the
    whole point is to prove the sync happens on its own, driven by
    accounts.apps._sync_role_permissions on post_migrate (which the
    test runner triggers when it builds the test database, exactly as
    a real `manage.py migrate` does on a fresh deploy).
    """

    def test_teachers_group_has_question_permissions_without_setup_roles(
        self,
    ):

        group = Group.objects.get(name="Teachers")

        codenames = set(
            group.permissions.values_list(
                "codename",
                flat=True,
            )
        )

        self.assertEqual(
            codenames,
            {"view_question", "add_question", "change_question"},
        )

    def test_students_group_has_no_question_permissions(self):

        group = Group.objects.get(name="Students")

        self.assertFalse(
            group.permissions.filter(
                content_type__app_label="assessment",
                content_type__model="question",
            ).exists()
        )

    def test_a_newly_approved_teacher_can_open_the_question_bank(self):

        user = get_user_model().objects.create_user(
            username="permsync_teacher",
            email="permsync_teacher@example.com",
            password="AeroESP-Strong-2026",
        )

        TeacherProfile.objects.create(
            user=user,
            approval_status=TeacherProfile.ApprovalStatus.APPROVED,
        )

        self.assertTrue(
            user.has_perm("assessment.view_question")
        )

        self.client.force_login(user)

        response = self.client.get(
            reverse("teacher_questions:list")
        )

        self.assertEqual(response.status_code, 200)


class OwnIdentityRenderingTests(TestCase):
    """
    Every page must take the displayed name from the viewer's own
    record. The reported symptom was a pending teacher seeing the
    administrator's name as their own: teacher_pending.html is the only
    page a logged-in user reaches that extends public_base.html, which
    credits the developer by name in its footer, and the page carried no
    name of the signed-in user to contrast it with.
    """

    ADMIN_FULL_NAME = "Habib Ziashafiq"

    def setUp(self):

        self.admin = get_user_model().objects.create_superuser(
            username="site_admin",
            email="admin@example.com",
            password="AeroESP-Strong-2026",
            first_name="Habib",
            last_name="Ziashafiq",
        )

        self.teacher = get_user_model().objects.create_user(
            username="koshaarash",
            email="koshaarash@example.com",
            password="AeroESP-Strong-2026",
            first_name="Arash",
            last_name="Kosha",
        )
        self.teacher.selected_role = "TEACHER"
        self.teacher.save()

        self.teacher_profile = TeacherProfile.objects.create(
            user=self.teacher,
            university="Sharif University",
        )

        self.student = get_user_model().objects.create_user(
            username="student_one",
            email="student@example.com",
            password="AeroESP-Strong-2026",
            first_name="Sara",
            last_name="Student",
        )

    def test_pending_teacher_page_names_the_signed_in_user(self):

        self.client.force_login(self.teacher)

        response = self.client.get(
            reverse("accounts:teacher_pending")
        )
        body = response.content.decode()

        self.assertContains(response, "koshaarash")
        self.assertIn("Arash Kosha", body)

    def test_pending_teacher_page_does_not_present_admin_as_the_user(self):
        """
        The developer credit may still appear in the footer, but the
        page must also state whose account is signed in, so the credit
        cannot be read as the viewer's own name.
        """

        self.client.force_login(self.teacher)

        response = self.client.get(
            reverse("accounts:teacher_pending")
        )
        body = response.content.decode()

        signed_in_at = body.find("Signed in as")
        credit_at = body.find("Designed &amp; Developed by")

        self.assertNotEqual(
            signed_in_at, -1,
            "pending teacher page must say who is signed in",
        )

        if credit_at != -1:
            self.assertLess(
                signed_in_at,
                credit_at,
                "the viewer's own identity must appear before the "
                "developer credit",
            )

    def test_account_center_shows_the_viewers_own_name(self):

        for user, expected in (
            (self.teacher, "Arash Kosha"),
            (self.student, "Sara Student"),
            (self.admin, self.ADMIN_FULL_NAME),
        ):

            with self.subTest(user=user.username):

                self.client.force_login(user)

                response = self.client.get(
                    reverse("accounts:account_center")
                )
                body = response.content.decode()

                self.assertIn(expected, body)

                # Nobody but the admin should see the admin's name in
                # the profile-information block.
                if user is not self.admin:
                    profile_block = body.split("Profile information")[1]
                    profile_block = profile_block.split("Workspace")[0]
                    self.assertNotIn(
                        self.ADMIN_FULL_NAME,
                        profile_block,
                    )

    def test_no_view_writes_another_users_name(self):
        """
        Guards the other half of the original hypothesis: that the
        approve/promote flow wrote request.user onto the target. Names
        must be untouched by an admin approving someone.
        """

        original = (
            self.teacher.first_name,
            self.teacher.last_name,
        )

        self.teacher_profile.approval_status = (
            TeacherProfile.ApprovalStatus.APPROVED
        )
        self.teacher_profile.approved_by = self.admin
        self.teacher_profile.save()

        self.teacher.refresh_from_db()

        self.assertEqual(
            (self.teacher.first_name, self.teacher.last_name),
            original,
        )
        self.assertNotEqual(
            self.teacher.get_full_name(),
            self.ADMIN_FULL_NAME,
        )
