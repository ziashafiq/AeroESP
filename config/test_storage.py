"""
Static file naming must survive a build that runs in a different
configuration from the process that later serves requests.

Guards the regression that rendered the deployed site as unstyled
text: collectstatic wrote unhashed files while the running app asked
for hashed ones, so every stylesheet 404'd.
"""

import shutil
import tempfile

from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase, override_settings

from config.storage import ForgivingManifestStaticFilesStorage


class StaticStorageSelectionTests(SimpleTestCase):

    def test_backend_does_not_depend_on_the_environment(self):
        """
        A backend chosen from DJANGO_ENV differs between build and
        runtime on hosts whose panel variables are runtime-only.
        """

        backend = settings.STORAGES["staticfiles"]["BACKEND"]

        self.assertEqual(
            backend,
            "config.storage.ForgivingManifestStaticFilesStorage",
        )


class ForgivingFallbackTests(SimpleTestCase):

    def setUp(self):

        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(
            shutil.rmtree,
            self.root,
            ignore_errors=True,
        )

    def _storage(self):

        with override_settings(STATIC_ROOT=str(self.root)):
            return ForgivingManifestStaticFilesStorage(
                location=str(self.root)
            )

    def test_unhashed_name_is_used_when_nothing_was_collected(self):

        storage = self._storage()

        self.assertEqual(
            storage.stored_name("aeroesp/css/app.css"),
            "aeroesp/css/app.css",
        )

    def test_unhashed_name_is_used_when_the_hashed_file_is_absent(self):
        """
        The exact deployment failure: the source file is present, so a
        hash can be computed, but collectstatic never wrote the hashed
        copy. Emitting that name would 404.
        """

        source = self.root / "aeroesp" / "css"
        source.mkdir(parents=True)
        (source / "app.css").write_text("body { color: red }")

        storage = self._storage()

        name = storage.stored_name("aeroesp/css/app.css")

        self.assertEqual(
            name,
            "aeroesp/css/app.css",
            "a hashed name must not be emitted for a file that was "
            "never written",
        )

    def test_hashed_name_is_used_once_the_file_exists(self):

        source = self.root / "aeroesp" / "css"
        source.mkdir(parents=True)
        (source / "app.css").write_text("body { color: red }")

        storage = self._storage()

        hashed = storage.hashed_name("aeroesp/css/app.css")

        # Simulate what collectstatic writes alongside the original.
        (self.root / hashed).write_text("body { color: red }")

        self.assertEqual(
            storage.stored_name("aeroesp/css/app.css"),
            # stored_name normalises separators; hashed_name does not,
            # so on Windows the raw value still carries backslashes.
            hashed.replace("\\", "/"),
        )
