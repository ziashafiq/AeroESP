"""
The installable-app layer: manifest, service worker, and the rule that
decides which pages the worker is allowed to keep on the device.

The security-shaped tests here are the ones worth keeping. A service
worker cache is shared by everyone using that browser profile, so a
page stored while somebody was signed in would be readable by the next
person who opens the app offline.
"""

import json

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from config import pwa


User = get_user_model()


class ManifestTests(TestCase):

    def setUp(self):
        self.response = self.client.get(reverse("manifest"))
        self.data = json.loads(self.response.content.decode())

    def test_served_as_a_manifest(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(
            self.response["Content-Type"],
            "application/manifest+json",
        )

    def test_carries_the_fields_chrome_requires_to_offer_install(self):

        for field in (
            "name",
            "short_name",
            "start_url",
            "display",
            "icons",
        ):
            self.assertIn(field, self.data)

        self.assertEqual(self.data["display"], "standalone")
        self.assertEqual(self.data["start_url"], "/")

    def test_has_both_icon_sizes_the_install_prompt_needs(self):
        """
        Chrome will not offer "Add to Home Screen" without a 192px and
        a 512px PNG. Losing one is silent - the prompt simply never
        appears - so it is asserted rather than eyeballed.
        """

        sizes = {
            icon["sizes"]
            for icon in self.data["icons"]
            if icon.get("purpose", "any") == "any"
        }

        self.assertIn("192x192", sizes)
        self.assertIn("512x512", sizes)

        for icon in self.data["icons"]:
            self.assertEqual(icon["type"], "image/png")

    def test_offers_maskable_icons_as_well(self):

        purposes = {
            icon.get("purpose") for icon in self.data["icons"]
        }

        self.assertIn("maskable", purposes)

    def test_brand_colours(self):

        self.assertEqual(self.data["theme_color"], "#1878f2")
        self.assertEqual(self.data["background_color"], "#071926")

    def test_every_icon_url_points_at_a_static_file(self):
        """
        Under ManifestStaticFilesStorage these URLs are content-hashed.
        A stale or misspelled path yields a manifest that parses fine
        and installs an app with no icon.
        """

        for icon in self.data["icons"]:
            with self.subTest(icon=icon["src"]):
                self.assertTrue(icon["src"].startswith("/static/"))


class ServiceWorkerTests(TestCase):

    def setUp(self):
        self.response = self.client.get("/sw.js")
        self.body = self.response.content.decode()

    def test_served_from_the_root_as_javascript(self):

        self.assertEqual(self.response.status_code, 200)
        self.assertIn("javascript", self.response["Content-Type"])
        self.assertEqual(
            self.response["Service-Worker-Allowed"],
            "/",
        )

    def test_is_never_cached_by_the_http_layer(self):
        """
        Browsers decide an update exists by byte-comparing this script.
        An HTTP cache in front of it pins users to the old worker.
        """

        cache_control = self.response["Cache-Control"]

        self.assertIn("no-cache", cache_control)
        self.assertIn("max-age=0", cache_control)

    def test_cache_names_are_scoped_to_a_build(self):

        self.assertIn('BUILD = "' + pwa.build_id() + '"', self.body)
        self.assertIn("aeroesp-assets-", self.body)
        self.assertIn("aeroesp-pages-", self.body)

    def test_activate_deletes_caches_from_previous_builds(self):
        """
        This is the anti-staleness mechanism: the cache name contains
        the build id, so after a deploy every older cache fails the
        keep test and is dropped.
        """

        self.assertIn("caches.delete(name)", self.body)
        self.assertIn("skipWaiting", self.body)
        self.assertIn("clients.claim", self.body)

    def test_precaches_the_offline_page_and_the_core_assets(self):

        self.assertIn('OFFLINE_URL = "/offline/"', self.body)

        for url in pwa.precache_urls():
            with self.subTest(url=url):
                self.assertIn(url, self.body)

    def test_has_a_fetch_handler(self):
        """Required before Chrome treats the site as installable."""

        self.assertIn('addEventListener("fetch"', self.body)

    def test_only_get_requests_are_intercepted(self):

        self.assertIn('request.method !== "GET"', self.body)

    def test_the_build_id_tracks_the_precache_contents(self):
        """
        Same inputs, same id - otherwise every request would invent a
        new cache and the worker would re-download the site forever.
        """

        self.assertEqual(pwa.build_id(), pwa.build_id())
        self.assertEqual(len(pwa.build_id()), 12)


class OfflinePageTests(TestCase):

    def test_renders_for_anonymous_visitors(self):

        response = self.client.get(reverse("offline"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "You are offline")

    def test_shows_nothing_about_the_signed_in_user(self):
        """
        The worker stores one copy of this page at install time and
        serves it to whoever opens the app next, so it must not carry
        a name, a nav state, or anything else personal.
        """

        user = User.objects.create_user(
            username="offlineuser",
            email="offline@example.com",
            password="Offline-Pass-12345",
        )

        self.client.force_login(user)

        body = self.client.get(reverse("offline")).content.decode()

        self.assertNotIn("offlineuser", body)
        self.assertNotIn("offline@example.com", body)
        self.assertNotIn("Sign out", body)

    def test_does_not_depend_on_the_stylesheet_surviving(self):

        body = self.client.get(reverse("offline")).content.decode()

        self.assertIn("<style>", body)


class CacheableHeaderTests(TestCase):
    """
    The server, not the worker, decides what may be stored on a device.
    """

    HEADER = pwa.CACHEABLE_HEADER

    def setUp(self):
        self.user = User.objects.create_user(
            username="cacheuser",
            email="cache@example.com",
            password="Cache-Pass-12345",
        )

    def test_public_page_is_marked_for_an_anonymous_visitor(self):

        response = self.client.get(reverse("home"))

        self.assertEqual(response[self.HEADER], "1")

    def test_terms_is_marked(self):

        response = self.client.get(reverse("terms"))

        self.assertEqual(response[self.HEADER], "1")

    def test_the_same_page_is_not_marked_once_signed_in(self):
        """
        The home page renders the visitor's name and workspace links
        when they are signed in: identical URL, personalised body -
        which is exactly why the URL alone cannot decide this.
        """

        self.client.force_login(self.user)

        response = self.client.get(reverse("home"))

        self.assertNotIn(self.HEADER, response)

    def test_authenticated_areas_are_never_marked(self):

        self.client.force_login(self.user)

        for name in (
            "accounts:account_center",
            "learning:guide_hub",
        ):
            with self.subTest(url=name):
                response = self.client.get(reverse(name))

                self.assertNotIn(self.HEADER, response)

    def test_the_login_page_is_never_marked(self):

        response = self.client.get(reverse("accounts:login"))

        self.assertNotIn(self.HEADER, response)

    def test_post_responses_are_never_marked(self):

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "nobody", "password": "wrong"},
        )

        self.assertNotIn(self.HEADER, response)

    def test_the_allowlist_holds_only_public_view_names(self):
        """
        A guard against a name being added here casually later: these
        four are the only views an anonymous visitor can reach whose
        body carries nothing personal.
        """

        self.assertEqual(
            pwa.CACHEABLE_VIEW_NAMES,
            frozenset({"home", "terms", "help_list", "help_detail"}),
        )


class RegistrationScriptTests(TestCase):

    def test_registers_the_worker_on_the_public_shell(self):

        body = self.client.get(reverse("home")).content.decode()

        self.assertIn('rel="manifest"', body)
        self.assertIn("serviceWorker", body)
        self.assertIn('register("/sw.js"', body)

    def test_apple_touch_icon_is_present(self):
        """iOS ignores the manifest and reads this instead."""

        body = self.client.get(reverse("home")).content.decode()

        self.assertIn('rel="apple-touch-icon"', body)

    @override_settings(DEBUG=True)
    def test_not_registered_in_development(self):
        """
        The worker serves /static/ cache-first, and development URLs
        carry no content hash - so an edited stylesheet would keep its
        URL and the browser would go on serving the cached copy.
        """

        self.assertFalse(pwa.context(None)["PWA_ENABLED"])

    def test_registered_outside_development(self):

        self.assertTrue(pwa.context(None)["PWA_ENABLED"])


class DesktopBehaviourUnchangedTests(TestCase):
    """
    The brief was explicit that nothing about the existing desktop
    experience may change. The middleware is the only thing added here
    that touches an existing response.
    """

    def test_middleware_changes_neither_status_nor_body(self):

        with_middleware = self.client.get(reverse("home"))

        without = [
            m
            for m in settings.MIDDLEWARE
            if "PublicPageCacheHeaderMiddleware" not in m
        ]

        with override_settings(MIDDLEWARE=without):
            without_middleware = self.client.get(reverse("home"))

        self.assertEqual(
            with_middleware.status_code,
            without_middleware.status_code,
        )
        self.assertEqual(
            with_middleware.content,
            without_middleware.content,
        )

    def test_status_codes_of_the_public_pages_are_untouched(self):

        for name in ("home", "terms", "help_list"):
            with self.subTest(url=name):
                self.assertEqual(
                    self.client.get(reverse(name)).status_code,
                    200,
                )
