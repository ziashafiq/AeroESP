/* AeroESP service worker - rendered by config.pwa.service_worker.
   Do not edit a copy under static/: the precache URLs below are
   content-hashed and only resolvable at render time. */

"use strict";

const BUILD = "{{ build_id }}";

const ASSET_CACHE = `aeroesp-assets-${BUILD}`;
const PAGE_CACHE = `aeroesp-pages-${BUILD}`;

const OFFLINE_URL = "/offline/";

/* Rendered by the view; these carry a content hash in production. */
const PRECACHE = [OFFLINE_URL].concat({{ precache_json|safe }});

/* Only the server may decide a page is safe to store; see
   PublicPageCacheHeaderMiddleware. The worker cannot see the session
   cookie and must not guess from the URL. */
const CACHEABLE_HEADER = "x-aeroesp-cacheable";


self.addEventListener("install", (event) => {
    event.waitUntil(
        (async () => {
            const cache = await caches.open(ASSET_CACHE);

            /* Added one at a time rather than with addAll, which
               rejects the whole install if a single entry 404s and
               would leave the site with no worker at all. */
            await Promise.all(
                PRECACHE.map((url) =>
                    cache.add(new Request(url, { cache: "reload" }))
                        .catch(() => undefined)
                )
            );

            /* Take over immediately. Combined with the version-scoped
               cache names, this is what stops a deploy from leaving
               users on yesterday's assets. */
            await self.skipWaiting();
        })()
    );
});


self.addEventListener("activate", (event) => {
    event.waitUntil(
        (async () => {
            const keep = new Set([ASSET_CACHE, PAGE_CACHE]);

            const names = await caches.keys();

            await Promise.all(
                names
                    .filter(
                        (name) =>
                            name.startsWith("aeroesp-") && !keep.has(name)
                    )
                    .map((name) => caches.delete(name))
            );

            await self.clients.claim();
        })()
    );
});


/* Allows the page to ask for an immediate update after a deploy. */
self.addEventListener("message", (event) => {
    if (event.data === "aeroesp-skip-waiting") {
        self.skipWaiting();
    }
});


function isAsset(url) {
    return url.pathname.startsWith("/static/");
}


async function assetFirst(request) {
    const cache = await caches.open(ASSET_CACHE);

    const hit = await cache.match(request);

    if (hit) {
        return hit;
    }

    const response = await fetch(request);

    /* Static filenames carry a content hash, so a cached entry can
       never be stale - a changed file is a different URL. */
    if (response && response.ok && response.type === "basic") {
        cache.put(request, response.clone());
    }

    return response;
}


async function pageNetworkFirst(request) {
    const cache = await caches.open(PAGE_CACHE);

    try {
        const response = await fetch(request);

        const allowed =
            response.ok &&
            response.headers.get(CACHEABLE_HEADER) === "1";

        if (allowed) {
            cache.put(request, response.clone());
        } else {
            /* The page stopped being public - drop any older copy
               rather than keeping it reachable offline. */
            cache.delete(request);
        }

        return response;
    } catch (error) {
        const hit = await cache.match(request);

        if (hit) {
            return hit;
        }

        const assets = await caches.open(ASSET_CACHE);
        const offline = await assets.match(OFFLINE_URL);

        if (offline) {
            return offline;
        }

        throw error;
    }
}


self.addEventListener("fetch", (event) => {
    const request = event.request;

    if (request.method !== "GET") {
        return;
    }

    const url = new URL(request.url);

    if (url.origin !== self.location.origin) {
        return;
    }

    if (isAsset(url)) {
        event.respondWith(assetFirst(request));
        return;
    }

    if (request.mode === "navigate") {
        event.respondWith(pageNetworkFirst(request));
        return;
    }

    /* Everything else - dashboards, the admin, the review app, every
       JSON endpoint - is left entirely alone. Not caching it is the
       point: none of it is safe to keep on a shared device. */
});
