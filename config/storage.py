import logging

from whitenoise.storage import CompressedManifestStaticFilesStorage


logger = logging.getLogger(__name__)


class ForgivingManifestStaticFilesStorage(
    CompressedManifestStaticFilesStorage
):
    """
    Content-hashed static filenames that degrade instead of 404ing.

    collectstatic renames every file to include a hash of its contents
    (app.css -> app.4f3a2b1c.css), so an edited file gets a new URL and
    browsers fetch it immediately. That is what makes a one-year cache
    header safe: with stable names, a changed logo keeps its URL and
    visitors keep the copy they already cached.

    The guard below exists because a hashed name is worthless unless
    the hashed file was actually written. That is not a hypothetical:
    hosts whose panel environment variables exist only at runtime run
    collectstatic in a different configuration from the one that later
    serves the pages, and the app then asks for filenames that
    collectstatic never produced - every stylesheet 404s and the site
    renders as unstyled text.

    This class must therefore be used unconditionally, in every
    environment, so that the build and the running app always agree.
    """

    manifest_strict = False

    def stored_name(self, name):

        try:
            hashed = super().stored_name(name)

        except ValueError:
            # Absent from the manifest and from STATIC_ROOT: nothing to
            # hash against, so serve the path as written.
            logger.warning(
                "Static file %r has no hashed name; serving the "
                "unhashed path. Run collectstatic if this is "
                "unexpected.",
                name,
            )

            return name

        if hashed != name and not self.exists(hashed):

            logger.warning(
                "Hashed static file %r does not exist; falling back "
                "to %r. This usually means collectstatic ran with a "
                "different staticfiles backend than the one serving "
                "requests.",
                hashed,
                name,
            )

            return name

        return hashed
