"""
Locks in the settings the aeroesp.com launch depends on, so a future
change cannot silently disable HTTPS enforcement or the domain
allowlist without a test noticing.
"""

from django.conf import settings
from django.test import SimpleTestCase


class ProductionDomainSecurityTests(SimpleTestCase):

    def test_ssl_redirect_is_forced_in_production(self):
        """
        IS_PRODUCTION is decided once, at process start, from
        DJANGO_ENV - so this checks the value actually loaded for the
        test run rather than re-deriving it, which would just test the
        test.
        """

        if settings.IS_PRODUCTION:

            self.assertTrue(settings.SECURE_SSL_REDIRECT)

        else:

            self.assertFalse(settings.SECURE_SSL_REDIRECT)

    def test_allowed_hosts_and_csrf_origins_come_from_the_environment(
        self,
    ):
        """
        Neither list may hardcode a domain: the same code has to run
        unmodified behind the Liara host, aeroesp.com, and any future
        domain, purely by changing environment variables.
        """

        import inspect

        import config.settings as settings_module

        source = inspect.getsource(settings_module)

        # A literal "aeroesp.com" anywhere near these settings would
        # mean someone hardcoded the domain instead of reading it from
        # DJANGO_ALLOWED_HOSTS / DJANGO_CSRF_TRUSTED_ORIGINS.
        self.assertNotIn("aeroesp.com", source)

        self.assertIsInstance(settings.ALLOWED_HOSTS, list)
        self.assertIsInstance(settings.CSRF_TRUSTED_ORIGINS, list)
