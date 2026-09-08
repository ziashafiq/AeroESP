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
        "register/",
        views.register,
        name="register",
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
        "preferences/palette/",
        views.set_color_palette,
        name="set_color_palette",
    ),

    path(
        "preferences/avatar/",
        views.set_avatar,
        name="set_avatar",
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

    # NOTE: password reset lives in accounts/password_urls.py
    # (mounted at /accounts/password/). It is the single canonical
    # flow, with the email/subject templates already wired up.

    path(
        "verify-email/",
        views.verify_email,
        name="verify_email",
    ),

    path(
        "verify-email/resend/",
        views.resend_verification_code,
        name="resend_verification_code",
    ),

]