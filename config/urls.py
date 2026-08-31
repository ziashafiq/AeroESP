from django.contrib import admin
from django.urls import (
    include,
    path,
)
from django.views.generic import RedirectView

from accounts import views as account_views

from .health import (
    health_live,
    health_ready,
)


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
        "readyz/",
        health_ready,
        name="health_ready",
    ),

    path(
        "favicon.ico",
        RedirectView.as_view(
            url=(
                "/static/aeroesp/brand/final/"
                "aeroesp-app-icon.png?v=ui17"
            ),
            permanent=False,
        ),
    ),

    path(
        "admin/",
        admin.site.urls,
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


handler400 = "accounts.views.error_400"
handler403 = "accounts.views.error_403"
handler404 = "accounts.views.error_404"
handler500 = "accounts.views.error_500"