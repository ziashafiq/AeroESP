"""
Which database hosts count as private, and therefore what sslmode the
project asks for.

Guards a deploy-breaking regression: requiring TLS for every non-local
host made the app unable to reach a database on the provider's own
private network, which answers
"server does not support SSL, but SSL was required".
"""

from django.test import SimpleTestCase

from config.settings import _is_private_db_host


class PrivateDatabaseHostTests(SimpleTestCase):

    PRIVATE = [
        ("aeroesp", "Liara internal service name"),
        ("172.17.191.2", "Liara private IP"),
        ("db", "docker compose service"),
        ("postgres.default.svc.cluster.local", "kubernetes DNS"),
        ("database.internal", "provider internal suffix"),
        ("10.0.0.5", "RFC 1918"),
        ("192.168.1.20", "RFC 1918"),
        ("localhost", "local development"),
        ("127.0.0.1", "loopback"),
        ("::1", "IPv6 loopback"),
        ("/var/run/postgresql", "unix socket path"),
        ("", "unix socket"),
    ]

    PUBLIC = [
        ("dpg-abc123-a.oregon-postgres.render.com", "Render external"),
        ("ep-cool-lab.eu-central-1.aws.neon.tech", "Neon external"),
        ("db.abcdefgh.supabase.co", "Supabase external"),
        ("aeroesp.example.com", "public hostname"),
        ("93.184.216.34", "public IPv4"),
    ]

    def test_private_hosts_do_not_force_tls(self):

        for host, description in self.PRIVATE:

            with self.subTest(host=host, case=description):

                self.assertTrue(
                    _is_private_db_host(host),
                    f"{host!r} ({description}) should be treated as "
                    "private, otherwise sslmode=require breaks the "
                    "connection",
                )

    def test_public_hosts_still_require_tls(self):

        for host, description in self.PUBLIC:

            with self.subTest(host=host, case=description):

                self.assertFalse(
                    _is_private_db_host(host),
                    f"{host!r} ({description}) is reached over the "
                    "internet and must keep sslmode=require",
                )

    def test_case_and_whitespace_are_ignored(self):

        self.assertTrue(_is_private_db_host("  AeroESP  "))
        self.assertFalse(_is_private_db_host("  DB.Example.COM  "))
