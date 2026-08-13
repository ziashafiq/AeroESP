from django.contrib.auth import views as auth_views
from django.urls import path

from . import views


app_name = "accounts"


urlpatterns = [

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        views.user_logout,
        name="logout",
    ),

    path(
        "account/",
        views.account_center,
        name="account_center",
    ),

    path(
        "redirect/",
        views.role_redirect,
        name="role_redirect",
    ),

    path(
        "student/dashboard/",
        views.student_dashboard,
        name="student_dashboard",
    ),

    path(
        "teacher/dashboard/",
        views.teacher_dashboard,
        name="teacher_dashboard",
    ),

    path(
        "teacher/pending/",
        views.teacher_pending,
        name="teacher_pending",
    ),
]