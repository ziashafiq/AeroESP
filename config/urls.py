from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.shortcuts import redirect
# Aliased: django.conf.urls.static.static (imported above, for serving
# MEDIA in development) has the same name and a different job.
from django.templatetags.static import static as static_url
from django.urls import (
    include,
    path,
)

from accounts import views as account_views

from .health import (
    health_live,
    health_ready,
)
from . import pwa
from .seo_views import robots_txt
from .sitemaps import sitemaps


urlpatterns = [

    path(
        "",
        account_views.home,
        name="home",
    ),

    path(
        "healthz/",
        health_live,
        name="health_live",
    ),

    path(
        "terms/",
        account_views.terms,
        name="terms",
    ),

    path(
        "help/",
        include(
            "accounts.help_urls"
        ),
    ),

    path(
        "readyz/",
        health_ready,
        name="health_ready",
    ),

    path(
        "robots.txt",
        robots_txt,
        name="robots_txt",
    ),

    # Served from the root: a service worker may only control the
    # directory it is served from, so one under /static/ would be
    # confined to /static/. See config/pwa.py.
    path(
        "sw.js",
        pwa.service_worker,
        name="service_worker",
    ),

    path(
        "manifest.webmanifest",
        pwa.manifest,
        name="manifest",
    ),

    path(
        "offline/",
        pwa.offline,
        name="offline",
    ),

    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),

    # Resolved per request rather than hardcoded, so the redirect
    # points at the content-hashed filename and a replaced icon is
    # picked up instead of being served from cache for a year.
    path(
        "favicon.ico",
        lambda request: redirect(
            static_url(
                "aeroesp/brand/final/aeroesp-app-icon.png"
            )
        ),
    ),

    path(
        "admin/",
        admin.site.urls,
    ),

    # Serves the generated challenge images and the refresh endpoint.
    path(
        "captcha/",
        include(
            "accounts.captcha_urls"
        ),
    ),

    path(
        "accounts/password/",
        include(
            "accounts.password_urls"
        ),
    ),

    path(
        "accounts/",
        include(
            "accounts.urls"
        ),
    ),

    path(
        "learn/",
        include(
            "learning.urls"
        ),
    ),

    path(
        "teacher/exams/",
        include(
            "exams.urls"
        ),
    ),

    path(
        "student/exams/",
        include(
            "exams.student_urls"
        ),
    ),

    path(
        "teacher/",
        include(
            "assessment.teacher_urls"
        ),
    ),

    path(
        "expert-review/",
        include(
            "research_review.urls"
        ),
    ),

    path(
        "",
        include(
            "assessment.urls"
        ),
    ),

    path(
        "ai/",
        include(
            "intelligence.urls"
        ),
    ),
]


# In development Django itself serves user uploads.
# In production these are served by nginx / the platform.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )


handler400 = "accounts.views.error_400"
handler403 = "accounts.views.error_403"
handler404 = "accounts.views.error_404"
handler500 = "accounts.views.error_500"