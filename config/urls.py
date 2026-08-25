"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from accounts import views as account_views


urlpatterns = [
    path(
        "",
        account_views.home,
        name="home",
    ),

    path(
        "favicon.ico",
        RedirectView.as_view(
            url="/static/aeroesp/brand/final/aeroesp-app-icon.png?v=ui17",
            permanent=False,
        ),
    ),

    path("admin/", admin.site.urls),

    path(
        "accounts/",
        include("accounts.urls"),
    ),

    path(
        "learn/",
        include("learning.urls"),
    ),

    path(
    "teacher/exams/",
    include("exams.urls"),
    ),
    
    path(
    "student/exams/",
    include(
        "exams.student_urls"
    ),
    ),

    path(
        "teacher/",
        include("assessment.teacher_urls"),
    ),

    path(
        "",
        include("assessment.urls"),
    ),

    path(
        "ai/",
        include("intelligence.urls"),
    ),
]


handler403 = "accounts.views.error_403"
handler404 = "accounts.views.error_404"
handler500 = "accounts.views.error_500"
