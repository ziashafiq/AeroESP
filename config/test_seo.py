"""
robots.txt, sitemap.xml, and the canonical-URL tag: the pieces search
engines actually read.
"""

from django.test import TestCase, override_settings
from django.urls import reverse

from accounts.models import HelpGuide


class RobotsTxtTests(TestCase):

    def test_returns_plain_text(self):

        response = self.client.get(reverse("robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "text/plain",
        )

    def test_login_required_sections_are_disallowed(self):

        body = self.client.get(
            reverse("robots_txt")
        ).content.decode()

        for path in (
            "/admin/",
            "/accounts/",
            "/learn/",
            "/teacher/",
            "/student/",
            "/ai/",
        ):

            self.assertIn(f"Disallow: {path}", body)

    def test_public_pages_are_allowed(self):

        body = self.client.get(
            reverse("robots_txt")
        ).content.decode()

        self.assertIn("Allow: /terms/", body)
        self.assertIn("Allow: /help/", body)
        self.assertIn(
            "Allow: /expert-review/getting-started/",
            body,
        )

    def test_reviewer_onboarding_page_is_allowed_despite_its_prefix(
        self,
    ):
        """
        /expert-review/ as a whole is disallowed (everything else
        under it needs an active reviewer account), but the one public
        page under that prefix must still be crawlable. Per the
        robots.txt spec the longer, more specific rule wins regardless
        of line order, so this only holds if the Allow line for the
        getting-started page is actually more specific than the
        Disallow for the section.
        """

        body = self.client.get(
            reverse("robots_txt")
        ).content.decode()

        allow_line = "Allow: /expert-review/getting-started/"
        disallow_line = "Disallow: /expert-review/"

        self.assertIn(allow_line, body)
        self.assertIn(disallow_line, body)

        self.assertGreater(
            len(allow_line.split(": ", 1)[1]),
            len(disallow_line.split(": ", 1)[1]),
        )

    def test_references_the_sitemap(self):

        response = self.client.get(reverse("robots_txt"))

        self.assertIn(
            b"Sitemap: http",
            response.content,
        )
        self.assertIn(
            b"/sitemap.xml",
            response.content,
        )


class SitemapTests(TestCase):

    def test_returns_valid_xml_with_the_public_pages(self):

        response = self.client.get(reverse("sitemap"))

        self.assertEqual(response.status_code, 200)

        body = response.content.decode()

        self.assertIn("<urlset", body)

        for path in ("/", "/terms/", "/help/", "/quiz/"):
            self.assertIn(f"<loc>https://", body)

        self.assertIn(
            "/expert-review/getting-started/",
            body,
        )

    def test_login_required_pages_are_absent(self):

        body = self.client.get(
            reverse("sitemap")
        ).content.decode()

        for fragment in ("/learn/", "/teacher/", "/admin/", "/ai/"):
            self.assertNotIn(fragment, body)

    def test_published_help_guides_are_included(self):

        HelpGuide.objects.create(
            audience=HelpGuide.Audience.STUDENT,
            slug="sitemap-test-guide",
            title="Sitemap Test Guide",
        )

        body = self.client.get(
            reverse("sitemap")
        ).content.decode()

        self.assertIn("/help/sitemap-test-guide/", body)

    def test_unpublished_help_guides_are_excluded(self):

        HelpGuide.objects.create(
            audience=HelpGuide.Audience.STUDENT,
            slug="sitemap-draft-guide",
            title="Draft",
            is_published=False,
        )

        body = self.client.get(
            reverse("sitemap")
        ).content.decode()

        self.assertNotIn("sitemap-draft-guide", body)

    @override_settings(AEROESP_CANONICAL_HOST="aeroesp.example")
    def test_uses_the_canonical_domain_once_configured(self):

        body = self.client.get(
            reverse("sitemap")
        ).content.decode()

        self.assertIn("https://aeroesp.example/", body)


class CanonicalUrlTagTests(TestCase):

    def test_no_tag_when_canonical_host_is_unset(self):

        with self.settings(AEROESP_CANONICAL_HOST=""):

            response = self.client.get(reverse("home"))

            self.assertNotContains(response, 'rel="canonical"')

    @override_settings(AEROESP_CANONICAL_HOST="aeroesp.example")
    def test_tag_points_at_the_canonical_domain(self):

        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            '<link rel="canonical" href="https://aeroesp.example/">',
        )

    @override_settings(AEROESP_CANONICAL_HOST="aeroesp.example")
    def test_tag_reflects_the_current_path(self):

        response = self.client.get(reverse("terms"))

        self.assertContains(
            response,
            'href="https://aeroesp.example/terms/"',
        )
