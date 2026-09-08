"""
Progressive Web App plumbing: manifest, service worker, offline page.

Three things here are deliberate and easy to get wrong later.

1. The manifest and the service worker are rendered as *templates*, not
   shipped as flat files under ``static/``. They have to name other
   static assets, and under ``ManifestStaticFilesStorage`` those names
   carry a content hash that is only known at render time. A flat
   ``sw.js`` would have to hardcode ``/static/aeroesp/css/app.css`` and
   would precache a URL that 404s in production.

2. The service worker is served from the site root. A worker's default
   scope is the directory it is served from, so one living at
   ``/static/sw.js`` could only control ``/static/`` - useless. The
   ``Service-Worker-Allowed`` header is sent as well, which is what
   permits the wider scope if the URL ever moves.

3. The cache name embeds a build id derived from the precache list.
   Because those URLs are content-hashed, editing any precached asset
   changes the id, which changes the cache name, and ``activate``
   deletes every cache that is not the current one. That is the whole
   answer to "users see a stale version after a deploy", together with
   network-first navigation below.
"""

import hashlib
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET


# Assets worth having available offline. Kept short on purpose: every
# entry has to download successfully or the whole install fails.
PRECACHE_ASSETS = [
    "aeroesp/css/app.css",
    "aeroesp/js/app.js",
    "aeroesp/brand/pwa/icon-192.png",
    "aeroesp/brand/final/aeroesp-logo-light.png",
    "aeroesp/brand/final/aeroesp-logo-dark.png",
]


# Public, non-personalised pages the worker may keep a copy of. This is
# only half the guard - the response must *also* carry the header set by
# PublicPageCacheHeaderMiddleware, which is only added for anonymous
# requests. Both must agree before anything is written to the cache.
CACHEABLE_VIEW_NAMES = frozenset({
    "home",
    "terms",
    "help_list",
    "help_detail",
})


CACHEABLE_HEADER = "X-AeroESP-Cacheable"


def precache_urls():
    """Resolved (hashed, in production) URLs for the precache list."""

    return [static(path) for path in PRECACHE_ASSETS]


def build_id():
    """
    Short digest of the precache URLs.

    Under ManifestStaticFilesStorage those URLs contain a content hash,
    so this changes exactly when a precached asset changes and stays
    stable across restarts otherwise. In development the storage falls
    back to unhashed names, so the id is constant - which is correct,
    because WHITENOISE_MAX_AGE is 0 there and nothing is being cached
    aggressively anyway.
    """

    joined = "\n".join(precache_urls()).encode("utf-8")

    return hashlib.sha256(joined).hexdigest()[:12]


@require_GET
@cache_control(max_age=0, no_cache=True, must_revalidate=True)
def manifest(request):

    response = render(
        request,
        "pwa/manifest.webmanifest",
        content_type="application/manifest+json",
    )

    return response


@require_GET
@cache_control(max_age=0, no_cache=True, must_revalidate=True)
def service_worker(request):
    """
    The worker script itself is never cached by the HTTP layer.

    Browsers byte-compare the script to decide whether an update is
    available, so an HTTP cache in front of it would pin users to an old
    worker - the exact staleness this file exists to prevent.
    """

    response = render(
        request,
        "pwa/sw.js",
        {
            "build_id": build_id(),
            # Serialised here rather than looped over in the template:
            # escapejs would render every "-" in a filename as -,
            # which is valid JavaScript but unreadable in the shipped
            # file and awkward to assert against.
            "precache_json": json.dumps(precache_urls(), indent=4),
        },
        content_type="text/javascript",
    )

    # Only meaningful if the script ever moves off the root, but a
    # worker silently failing to register is miserable to diagnose.
    response["Service-Worker-Allowed"] = "/"

    return response


@require_GET
def offline(request):
    """Shown when a navigation fails and nothing is cached for it."""

    return render(request, "pwa/offline.html")


class PublicPageCacheHeaderMiddleware:
    """
    Marks a response as safe for the service worker to store.

    The worker refuses to cache any navigation without this header, so
    the decision about what may sit in a shared on-device cache is made
    here, on the server, where the request's identity is actually known
    - not in JavaScript guessing from a URL. A signed-in user loading
    the home page gets no header and therefore no cached copy, which is
    what keeps a personalised page out of a cache the next visitor to
    that device could read.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)

        if request.method != "GET":
            return response

        if response.status_code != 200:
            return response

        user = getattr(request, "user", None)

        if user is None or user.is_authenticated:
            return response

        match = getattr(request, "resolver_match", None)

        if match is None or match.url_name not in CACHEABLE_VIEW_NAMES:
            return response

        response[CACHEABLE_HEADER] = "1"

        return response


def context(request):
    """
    Template context for the PWA head tags and the registration script.

    Registration is off under DEBUG. The worker serves ``/static/``
    cache-first, and in development those filenames carry no content
    hash, so an edited stylesheet would keep its URL and the browser
    would go on serving the copy in the worker's cache - an edit that
    silently does nothing. ``AEROESP_ENABLE_PWA=1`` forces it on for
    deliberate local testing.
    """

    from django.conf import settings

    import os

    enabled = (
        not settings.DEBUG
        or os.environ.get("AEROESP_ENABLE_PWA") == "1"
    )

    return {"PWA_ENABLED": enabled}
