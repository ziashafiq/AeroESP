"""
Selectable accent palettes: the contrast guarantees, where the choice
is stored, and the rules for who may change whose.

The contrast tests parse the real stylesheet rather than a copy of the
numbers. A palette added later with an eyeballed colour fails here.
"""

import colorsys
import pathlib
import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()

CSS = (
    pathlib.Path(settings.BASE_DIR)
    / "static" / "aeroesp" / "css" / "app.css"
).read_text(encoding="utf-8")

JS = (
    pathlib.Path(settings.BASE_DIR)
    / "static" / "aeroesp" / "js" / "app.js"
).read_text(encoding="utf-8")


WHITE = (255, 255, 255)
DARK_SURFACE = (11, 27, 45)          # --theme-surface, dark

PALETTES = ["skyline", "copper", "indigo", "verdigris", "slate"]


def parse_hex(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb):
    def channel(c):
        c = c / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)

    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a, b):
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)

    return (hi + 0.05) / (lo + 0.05)


def tokens_for(selector):
    """
    The custom properties in effect for a selector.

    Several selectors have more than one rule block in this stylesheet
    (:root carries the design tokens near the top and the theme tokens
    much further down), so the blocks are merged in source order the
    way the cascade would resolve them.
    """

    pattern = re.compile(
        r"(?:^|[\s}])" + re.escape(selector) + r"\s*\{(.*?)\}",
        re.S | re.M,
    )

    blocks = pattern.findall(CSS)

    assert blocks, f"no rule found for {selector}"

    tokens = {}

    for block in blocks:
        tokens.update(
            re.findall(r"(--[a-z-]+):\s*([^;]+);", block)
        )

    return tokens


class PaletteContrastTests(TestCase):
    """
    WCAG AA, checked against the surface each token actually sits on.

    Only --theme-accent-strong and the gradient stops carry text or
    interactive meaning. --theme-accent is decorative - 6-30% alpha
    washes, glows, hover tints - and nothing in the interface is
    legible only because of it, so it is held to appearance rather
    than to a contrast floor.
    """

    def test_accent_text_clears_aa_in_light_mode(self):

        for palette in PALETTES:
            with self.subTest(palette=palette):

                tokens = tokens_for(f'html[data-palette="{palette}"]')

                ratio = contrast_ratio(
                    parse_hex(tokens["--theme-accent-strong"]),
                    WHITE,
                )

                self.assertGreaterEqual(
                    ratio,
                    4.5,
                    f"{palette}: accent text is {ratio:.2f}:1 on white",
                )

    def test_accent_text_clears_aa_in_dark_mode(self):

        for palette in PALETTES:
            with self.subTest(palette=palette):

                tokens = tokens_for(
                    f'html[data-palette="{palette}"][data-theme="dark"]'
                )

                ratio = contrast_ratio(
                    parse_hex(tokens["--theme-accent-strong"]),
                    DARK_SURFACE,
                )

                self.assertGreaterEqual(
                    ratio,
                    4.5,
                    f"{palette}: accent text is {ratio:.2f}:1 on the "
                    f"dark surface",
                )

    def test_gradient_buttons_can_carry_their_white_label(self):
        """
        Primary buttons are a gradient with `color: #ffffff`. The
        lighter stop is the worst case and it is the one that has to
        clear AA - a brighter, prettier fill silently fails here.
        """

        for palette in PALETTES:
            for suffix in ("", '[data-theme="dark"]'):
                with self.subTest(palette=palette, mode=suffix or "light"):

                    tokens = tokens_for(
                        f'html[data-palette="{palette}"]{suffix}'
                    )

                    for stop in ("a", "b"):
                        ratio = contrast_ratio(
                            parse_hex(
                                tokens[f"--theme-accent-grad-{stop}"]
                            ),
                            WHITE,
                        )

                        self.assertGreaterEqual(
                            ratio,
                            4.5,
                            f"{palette} gradient stop {stop} is "
                            f"{ratio:.2f}:1 against a white label",
                        )

    def test_the_base_tokens_clear_aa_too(self):
        """
        :root and the dark block are what an unset data-palette falls
        back to, so they carry the same obligation as a named palette.
        """

        light = tokens_for(":root")
        dark = tokens_for('html[data-theme="dark"]')

        self.assertGreaterEqual(
            contrast_ratio(
                parse_hex(light["--theme-accent-strong"]), WHITE
            ),
            4.5,
        )
        self.assertGreaterEqual(
            contrast_ratio(
                parse_hex(dark["--theme-accent-strong"]), DARK_SURFACE
            ),
            4.5,
        )


class PaletteTokenTests(TestCase):

    REQUIRED = [
        "--theme-accent",
        "--theme-accent-rgb",
        "--theme-accent-strong",
        "--theme-accent-strong-rgb",
        "--theme-accent-grad-a",
        "--theme-accent-grad-b",
    ]

    def test_every_palette_defines_the_full_set_in_both_schemes(self):

        for palette in PALETTES:
            for suffix in ("", '[data-theme="dark"]'):
                with self.subTest(palette=palette, mode=suffix or "light"):

                    tokens = tokens_for(
                        f'html[data-palette="{palette}"]{suffix}'
                    )

                    for name in self.REQUIRED:
                        self.assertIn(name, tokens)

    def test_the_rgb_triples_match_their_hex_counterparts(self):
        """
        The rgba() call sites read the triple, the solid ones read the
        hex. If they drift apart a palette gets two different accents
        in the same view.
        """

        for palette in PALETTES:
            for suffix in ("", '[data-theme="dark"]'):
                with self.subTest(palette=palette, mode=suffix or "light"):

                    tokens = tokens_for(
                        f'html[data-palette="{palette}"]{suffix}'
                    )

                    for base in ("--theme-accent",
                                 "--theme-accent-strong"):
                        expected = parse_hex(tokens[base])

                        triple = tuple(
                            int(part.strip())
                            for part in tokens[f"{base}-rgb"].split(",")
                        )

                        self.assertEqual(expected, triple, base)

    def test_the_default_palette_keeps_todays_decorative_blue(self):
        """
        The brief was explicit that the current blue stays default.
        Its text token did move - from 3.15:1 to AA - but the colour
        the interface is washed in did not.
        """

        tokens = tokens_for('html[data-palette="skyline"]')
        dark = tokens_for('html[data-palette="skyline"][data-theme="dark"]')

        self.assertEqual(tokens["--theme-accent"].strip(), "#48b9e8")
        self.assertEqual(dark["--theme-accent"].strip(), "#55c7ef")

    def test_no_accent_colour_is_left_hardcoded_in_the_stylesheet(self):
        """
        What makes a palette switch reach the whole interface.

        Written as a property rather than a list of known literals,
        because a list is exactly what let #087eae survive the first
        pass: it sat one character away from the #087fae that was
        being searched for, inside a dark-mode [class*="primary"]
        catch-all with !important, and repainted every primary button
        blue no matter which palette was chosen.

        The property: no saturated mid-tone blue may appear outside
        the token definitions. Pale tints and near-navy darks are left
        alone - those belong to the surface system, not the accent.
        """

        body = CSS

        # Where literals legitimately live.
        body = re.sub(
            r'html\[data-palette=[^{]*\{[^}]*\}', "", body, flags=re.S
        )
        body = re.sub(
            r"\.palette-[a-z]+ \.palette-swatch \{[^}]*\}", "", body
        )
        for token_block in (
            r":root \{[^}]*--theme-accent-rgb[^}]*\}",
            r'html\[data-theme="dark"\] \{[^}]*--theme-accent-rgb[^}]*\}',
        ):
            body = re.sub(token_block, "", body, flags=re.S)

        offenders = []

        def check(rgb, literal):
            hue, lum, sat = colorsys.rgb_to_hls(
                *[c / 255 for c in rgb]
            )

            if (
                188 <= hue * 360 <= 216
                and sat >= 0.60
                and 0.30 <= lum <= 0.80
            ):
                offenders.append(literal)

        for match in re.finditer(r"#([0-9a-fA-F]{6})", body):
            value = match.group(1).lower()
            check(
                tuple(int(value[i:i + 2], 16) for i in (0, 2, 4)),
                match.group(0),
            )

        for match in re.finditer(
            r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,",
            body,
        ):
            check(
                tuple(int(g) for g in match.groups()),
                match.group(0),
            )

        self.assertEqual(
            sorted(set(offenders)),
            [],
            "these blues would stay put while the palette moved",
        )


class WhiteLabelContrastTests(TestCase):
    """
    A guard against a mistake made while converting the hardcoded
    literals: --theme-accent-strong is solved for reading as text *on*
    a surface, which in dark mode makes it bright. Filling a button
    with it and putting a white label on top inverts the requirement
    and fails outright. Only the gradient pair is solved for
    white-on-fill, and it is the only accent role a white label may
    sit on.
    """

    def test_no_rule_puts_a_white_label_on_a_bare_accent_fill(self):

        offenders = []

        for block in re.split(r"(?<=\})", CSS):

            if "{" not in block:
                continue

            body = block.split("{", 1)[1]

            if not re.search(
                r"color:\s*#(?:fff|ffffff)", body, re.I
            ):
                continue

            if re.search(
                r"(?:background|background-color|background-image)"
                r"\s*:[^;]*var\(--theme-accent(?:-strong)?\)",
                body,
                re.S,
            ):
                offenders.append(
                    " ".join(block.split("{")[0].split())[:80]
                )

        self.assertEqual(offenders, [])

    def test_no_gradient_repeats_one_accent_role_for_both_stops(self):
        """
        Two identical stops mean a real gradient was flattened during
        conversion - and flattened onto the wrong role at that.
        """

        collapsed = re.findall(
            r"linear-gradient\([^)]*var\(--theme-accent(?:-strong)?\)"
            r"[^)]*var\(--theme-accent(?:-strong)?\)[^)]*\)",
            CSS,
            re.S,
        )

        self.assertEqual(collapsed, [])


class PaletteStorageTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="palettist",
            email="palettist@example.com",
            password="Palette-Pass-12345",
        )

    def test_new_users_start_on_the_default(self):

        self.assertEqual(self.user.color_palette, "skyline")

    def test_a_signed_in_user_can_change_their_palette(self):

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:set_color_palette"),
            {"palette": "verdigris"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

        self.user.refresh_from_db()
        self.assertEqual(self.user.color_palette, "verdigris")

    def test_an_unknown_palette_is_rejected_rather_than_stored(self):
        """
        Whatever is stored here is rendered straight into the
        data-palette attribute, so the set of accepted values has to
        be closed.
        """

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("accounts:set_color_palette"),
            {"palette": '"><script>alert(1)</script>'},
        )

        self.assertEqual(response.status_code, 400)

        self.user.refresh_from_db()
        self.assertEqual(self.user.color_palette, "skyline")

    def test_anonymous_visitors_cannot_write_a_palette(self):

        response = self.client.post(
            reverse("accounts:set_color_palette"),
            {"palette": "copper"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response["Location"])

    def test_the_endpoint_refuses_get(self):

        self.client.force_login(self.user)

        response = self.client.get(
            reverse("accounts:set_color_palette")
        )

        self.assertEqual(response.status_code, 405)

    def test_a_user_can_only_ever_change_their_own(self):
        """
        The view takes no user id: it filters on request.user.pk. This
        asserts the property that makes that safe.
        """

        other = User.objects.create_user(
            username="someoneelse",
            email="someoneelse@example.com",
            password="Other-Pass-12345",
        )

        self.client.force_login(self.user)

        self.client.post(
            reverse("accounts:set_color_palette"),
            {"palette": "indigo"},
        )

        other.refresh_from_db()
        self.assertEqual(other.color_palette, "skyline")


class PaletteRenderingTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="renderer",
            email="renderer@example.com",
            password="Render-Pass-12345",
        )

    def test_a_signed_in_users_palette_is_stamped_before_first_paint(self):
        """
        Rendered into <html> by the server rather than applied by
        script, so there is no flash of the default accent.
        """

        self.user.color_palette = "copper"
        self.user.save(update_fields=["color_palette"])

        self.client.force_login(self.user)

        body = self.client.get(
            reverse("accounts:account_center")
        ).content.decode()

        self.assertIn('data-palette="copper"', body)
        self.assertIn('data-palette-source="user"', body)

    def test_anonymous_pages_leave_the_palette_to_the_bootstrap(self):

        body = self.client.get(reverse("home")).content.decode()

        self.assertNotIn('data-palette-source="user"', body)
        self.assertIn("aeroesp-palette", body)

    def test_the_picker_is_rendered_with_every_palette(self):

        body = self.client.get(reverse("home")).content.decode()

        for palette in PALETTES:
            with self.subTest(palette=palette):
                self.assertIn(f'data-palette-option="{palette}"', body)

    def test_the_save_endpoint_is_offered_only_to_signed_in_users(self):

        anonymous = self.client.get(reverse("home")).content.decode()
        self.assertNotIn("data-palette-endpoint", anonymous)

        self.client.force_login(self.user)

        signed_in = self.client.get(
            reverse("accounts:account_center")
        ).content.decode()
        self.assertIn("data-palette-endpoint", signed_in)

    def test_the_reviewer_app_gets_the_guarded_bootstrap_too(self):
        """
        research_review/base.html carried its own copy of the original
        unguarded bootstrap, so the WebView fix from 0740fe0 never
        reached the reviewers. All three shells now share one include.
        """

        source = (
            pathlib.Path(settings.BASE_DIR)
            / "research_review" / "templates" / "research_review"
            / "base.html"
        ).read_text(encoding="utf-8")

        self.assertIn("aeroesp/_theme_bootstrap.html", source)
        self.assertNotIn("localStorage.getItem", source)


class ThemeEngineScopeTests(TestCase):
    """
    A regression guard for a live bug: the theme engine used to sit in
    its own IIFE while the sidebar handlers at the end of it referenced
    body, menuButton, sidebar and closeSidebar - const declarations
    belonging to the first IIFE. `if (menuButton && sidebar)` threw
    ReferenceError on every page load, so Escape-to-close and the
    back/forward reset were dead. Chrome confirmed it:
    "menuButton is not defined".
    """

    def test_the_script_is_a_single_scope(self):

        opens = len(re.findall(r"^\(\(\) => \{", JS, re.M))

        self.assertEqual(
            opens,
            1,
            "app.js has more than one top-level IIFE; the sidebar "
            "handlers at the end read declarations from the first one",
        )

    def test_the_names_the_tail_depends_on_are_declared_above_it(self):

        for name in ("body", "menuButton", "sidebar", "closeSidebar"):
            with self.subTest(name=name):

                declaration = re.search(
                    rf"^\s*(?:const|let|var|function)\s+{name}\b",
                    JS,
                    re.M,
                )

                self.assertIsNotNone(declaration, name)

                last_use = JS.rfind(f"{name}")

                self.assertLess(
                    declaration.start(),
                    last_use,
                    f"{name} is used before it is declared",
                )

    def test_every_storage_access_stays_guarded(self):

        for match in re.finditer(r"localStorage\.(get|set)Item", JS):
            window = JS[max(0, match.start() - 400):match.start()]

            self.assertIn(
                "try {",
                window,
                "an unguarded localStorage access would throw in a "
                "WebView with site data blocked",
            )
