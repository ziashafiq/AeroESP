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

    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name=
            "registration/password_reset.html"
        ),
        name="password_reset",
    ),


    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name=
            "registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),


    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name=
            "registration/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),

    path(
        "verify-email/",
        views.verify_email,
        name="verify_email",
    ),

]