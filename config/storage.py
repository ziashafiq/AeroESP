import logging

from whitenoise.storage import CompressedManifestStaticFilesStorage


logger = logging.getLogger(__name__)


class ForgivingManifestStaticFilesStorage(
    CompressedManifestStaticFilesStorage
):
    """
    Content-hashed static filenames, without the 500s.

    collectstatic renames every file to include a hash of its contents
    (app.css -> app.4f3a2b1c.css), so an edited file gets a new URL and
    browsers fetch it immediately. That is what makes a one-year cache
    header safe: with stable names, a changed logo keeps its URL and
    visitors keep the copy they already cached.

    The default storage raises when a template references a file it
    cannot hash, which turns one stale reference into a completely
    broken page. Here that degrades to serving the unhashed path: the
    asset may be cached longer than intended, but the page renders.
    """

    manifest_strict = False

    def stored_name(self, name):

        try:
            return super().stored_name(name)

        except ValueError:
            # Raised when the file is absent from both the manifest and
            # STATIC_ROOT - a reference to something that no longer
            # exists, or a collectstatic that has not run yet.
            logger.warning(
                "Static file %r has no hashed name; serving the "
                "unhashed path. Run collectstatic if this is "
                "unexpected.",
                name,
            )

            return name

    def url(self, name, force=False):

        try:
            return super().url(name, force=force)

        except ValueError:
            logger.warning(
                "Could not build a hashed URL for static file %r.",
                name,
            )

            return super(
                CompressedManifestStaticFilesStorage,
                self,
            ).url(name)
