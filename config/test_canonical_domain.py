"""
CanonicalDomainMiddleware: redirects www and legacy hosts to the
canonical apex domain in a single 301 hop.
"""

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from config.middleware import CanonicalDomainMiddleware


def _ok(request):
    return HttpResponse("ok")


class CanonicalDomainMiddlewareTests(SimpleTestCase):

    def setUp(self):

        self.factory = RequestFactory()
        self.middleware = CanonicalDomainMiddleware(_ok)

    def _get(self, host, path="/some/page/?q=1"):

        request = self.factory.get(path)
        request.META["HTTP_HOST"] = host

        return self.middleware(request)

    @override_settings(
        AEROESP_CANONICAL_HOST="aeroesp.example",
        AEROESP_LEGACY_HOSTS=["aeroesp-app.liara.run"],
    )
    def test_www_redirects_to_the_apex_domain(self):

        response = self._get("www.aeroesp.example")

        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response["Location"],
            "https://aeroesp.example/some/page/?q=1",
        )

    @override_settings(
        AEROESP_CANONICAL_HOST="aeroesp.example",
        AEROESP_LEGACY_HOSTS=["aeroesp-app.liara.run"],
    )
    def test_legacy_platform_host_redirects_to_the_apex_domain(self):

        response = self._get("aeroesp-app.liara.run")

        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response["Location"],
            "https://aeroesp.example/some/page/?q=1",
        )

    @override_settings(
        AEROESP_CANONICAL_HOST="aeroesp.example",
        AEROESP_LEGACY_HOSTS=["aeroesp-app.liara.run"],
    )
    def test_the_canonical_host_itself_is_not_redirected(self):

        response = self._get("aeroesp.example")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"ok")

    @override_settings(
        AEROESP_CANONICAL_HOST="aeroesp.example",
        AEROESP_LEGACY_HOSTS=[],
    )
    def test_an_unrelated_host_is_left_alone(self):
        """
        Only www-of-canonical and explicitly listed legacy hosts
        redirect - anything else (a misconfigured DNS entry, a scanner
        probing random Host headers) is passed through untouched
        rather than silently redirected somewhere.
        """

        response = self._get("some-other-domain.example")

        self.assertEqual(response.status_code, 200)

    @override_settings(AEROESP_CANONICAL_HOST="")
    def test_is_a_no_op_when_no_canonical_host_is_configured(self):
        """
        Local development and any deploy without a custom domain yet
        must see zero behaviour change.
        """

        response = self._get("www.anything.example")

        self.assertEqual(response.status_code, 200)

    @override_settings(
        AEROESP_CANONICAL_HOST="aeroesp.example",
        AEROESP_LEGACY_HOSTS=["aeroesp-app.liara.run"],
    )
    def test_redirect_works_even_if_the_old_host_is_not_in_allowed_hosts(
        self,
    ):
        """
        The whole point: a host that was never added to ALLOWED_HOSTS
        must still 301 to the canonical domain instead of surfacing
        Django's DisallowedHost 400 page. Reads the raw Host header
        rather than request.get_host(), which enforces ALLOWED_HOSTS
        and would raise here first.
        """

        with self.settings(ALLOWED_HOSTS=["aeroesp.example"]):

            response = self._get("aeroesp-app.liara.run")

            self.assertEqual(response.status_code, 301)

    @override_settings(
        AEROESP_CANONICAL_HOST="aeroesp.example",
        AEROESP_LEGACY_HOSTS=["aeroesp-app.liara.run"],
    )
    def test_redirect_preserves_the_full_path_and_query_string(self):

        response = self._get(
            "www.aeroesp.example",
            path="/help/expert-reviewer-getting-started/?ref=email",
        )

        self.assertEqual(
            response["Location"],
            "https://aeroesp.example"
            "/help/expert-reviewer-getting-started/?ref=email",
        )
