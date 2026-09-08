"""
Profile avatars, and a template-syntax guard that came out of building
them.

Upload is deliberately not implemented: it needs file validation,
storage and a content-safety story that a profile picture does not
justify. The choice is one of nine names, and the value is checked
against the model's own choices before it is stored, because it ends
up naming a file under static/.
"""

import pathlib
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.template import engines
from django.test import TestCase
from django.urls import reverse


User = get_user_model()

BASE = pathlib.Path(settings.BASE_DIR)


class AvatarAssetTests(TestCase):

    def test_every_choice_but_the_initial_has_a_file(self):

        for value, _label in User.AVATAR_CHOICES:

            if value == User.AVATAR_INITIAL:
                continue

            with self.subTest(avatar=value):
                path = (
                    BASE / "static" / "aeroesp" / "avatars"
                    / f"{value}.svg"
                )

                self.assertTrue(path.exists(), path)

    def test_there_are_eight_marks_plus_the_initial(self):

        self.assertEqual(len(User.AVATAR_CHOICES), 9)

    def test_the_marks_carry_their_own_background(self):
        """
        They render through an img element, which CSS cannot reach
        inside, so each has to be legible on both the light and the
        dark surface on its own.
        """

        for value, _label in User.AVATAR_CHOICES:

            if value == User.AVATAR_INITIAL:
                continue

            with self.subTest(avatar=value):
                svg = (
                    BASE / "static" / "aeroesp" / "avatars"
                    / f"{value}.svg"
                ).read_text(encoding="utf-8")

                self.assertIn("<circle", svg)
                self.assertIn('r="32"', svg)
                self.assertIn("viewBox", svg)

    def test_no_stray_files_in_the_avatar_directory(self):
        """
        Anything here that is not a choice is unreachable, and
        anything missing would render a broken image.
        """

        on_disk = {
            path.stem
            for path in (
                BASE / "static" / "aeroesp" / "avatars"
            ).glob("*.svg")
        }

        expected = {
            value
            for value, _label in User.AVATAR_CHOICES
            if value != User.AVATAR_INITIAL
        }

        self.assertEqual(on_disk, expected)


class AvatarStorageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="avatarist",
            email="avatarist@example.com",
            password="Avatar-Pass-12345",
        )
        self.url = reverse("accounts:set_avatar")

    def test_accounts_start_on_their_initial(self):
        """
        The default is the behaviour every account had before this,
        so nobody's profile changes appearance on deploy.
        """

        self.assertEqual(self.user.avatar, User.AVATAR_INITIAL)

    def test_a_signed_in_user_can_choose_a_mark(self):

        self.client.force_login(self.user)

        response = self.client.post(self.url, {"avatar": "orbit"})

        self.assertEqual(response.status_code, 200)

        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, "orbit")

    def test_the_initial_is_a_real_choice_to_go_back_to(self):

        self.user.avatar = "radar"
        self.user.save(update_fields=["avatar"])

        self.client.force_login(self.user)
        self.client.post(self.url, {"avatar": "INITIAL"})

        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, User.AVATAR_INITIAL)

    def test_an_unknown_value_is_rejected(self):
        """
        The stored value names a file under static/, so the set of
        accepted values has to be closed.
        """

        self.client.force_login(self.user)

        for attempt in (
            "../../../etc/passwd",
            "nonexistent",
            "",
            "delta.svg",
        ):
            with self.subTest(attempt=attempt):
                response = self.client.post(
                    self.url, {"avatar": attempt}
                )

                self.assertEqual(response.status_code, 400)

                self.user.refresh_from_db()
                self.assertEqual(
                    self.user.avatar, User.AVATAR_INITIAL
                )

    def test_anonymous_visitors_cannot_write_one(self):

        response = self.client.post(self.url, {"avatar": "delta"})

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response["Location"])

    def test_a_user_can_only_change_their_own(self):

        other = User.objects.create_user(
            username="otherface",
            email="otherface@example.com",
            password="Other-Pass-12345",
        )

        self.client.force_login(self.user)
        self.client.post(self.url, {"avatar": "polaris"})

        other.refresh_from_db()
        self.assertEqual(other.avatar, User.AVATAR_INITIAL)


class AvatarRenderingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="zephyr",
            email="zephyr@example.com",
            password="Zephyr-Pass-12345",
        )
        self.client.force_login(self.user)

    def test_the_initial_is_shown_by_default(self):

        body = self.client.get(
            reverse("accounts:account_center")
        ).content.decode()

        self.assertIn("Z", body)
        self.assertNotIn("aeroesp/avatars/", body.split("picker")[0])

    def test_a_chosen_mark_replaces_the_initial(self):

        self.user.avatar = "turbine"
        self.user.save(update_fields=["avatar"])

        body = self.client.get(
            reverse("accounts:account_center")
        ).content.decode()

        self.assertIn("avatar-mark", body)
        self.assertIn("turbine", body)

    def test_the_picker_offers_every_choice(self):

        body = self.client.get(
            reverse("accounts:account_center")
        ).content.decode()

        for value, _label in User.AVATAR_CHOICES:
            with self.subTest(avatar=value):
                self.assertIn(f'data-avatar-option="{value}"', body)

    def test_one_implementation_renders_all_three_places(self):
        """
        The initial used to be written out by hand in three templates,
        which is how two of them end up disagreeing later.
        """

        shell = (
            BASE / "templates" / "aeroesp" / "base.html"
        ).read_text(encoding="utf-8")

        # Two display sites in the shell - sidebar and topbar - and
        # neither may spell out the initial itself.
        self.assertNotIn('username|slice:":1"', shell)
        self.assertEqual(shell.count("aeroesp/_avatar.html"), 2)

        centre = (
            BASE / "accounts" / "templates" / "accounts"
            / "account_center.html"
        ).read_text(encoding="utf-8")

        self.assertIn("aeroesp/_avatar.html", centre)

        # Exactly one remaining: the picker's own preview swatch,
        # which shows what "Initial" would look like rather than
        # displaying the current avatar.
        self.assertEqual(centre.count('username|slice:":1"'), 1)


class TemplateCommentSyntaxTests(TestCase):
    """
    A live bug found while building this: Django's {# #} is
    single-line only - the lexer's pattern is not DOTALL - so a
    multi-line one is not a comment at all. Its text renders straight
    into the page, and any {{ }} inside it is evaluated on the way.

    Two of these were live: approved teachers had a paragraph of
    explanatory prose sitting in their sidebar, and pending teachers
    had another above "Signed in as". Neither showed up in the earlier
    screenshot review, which only covered admin pages.
    """

    def test_the_lexer_really_does_ignore_multi_line_hash_comments(
        self,
    ):
        """
        Asserted rather than assumed, because the whole guard below
        rests on it.
        """

        rendered = engines["django"].from_string(
            "A{#\nnot actually a comment\n#}B"
        ).render({})

        self.assertIn("not actually a comment", rendered)

    def test_no_template_contains_a_multi_line_hash_comment(self):

        offenders = []

        for template in BASE.rglob("*.html"):

            if "staticfiles" in template.parts:
                continue
            if ".venv" in template.parts:
                continue

            source = template.read_text(
                encoding="utf-8", errors="replace"
            )

            for match in re.finditer(r"\{#", source):
                rest = source[match.start():]
                closer = rest.find("#}")

                if closer == -1 or "\n" in rest[:closer]:
                    line = source[:match.start()].count("\n") + 1
                    offenders.append(
                        f"{template.relative_to(BASE)}:{line}"
                    )

        self.assertEqual(
            offenders,
            [],
            "use {% comment %} for anything spanning a line break",
        )
