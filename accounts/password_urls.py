from django.contrib.auth import views
from django.urls import path

from .views import PasswordResetOrSupportView


urlpatterns = [

    # Templates and the graceful "no mail service" fallback live on
    # the view class; see accounts/views.py.
    path(
        "reset/",
        PasswordResetOrSupportView.as_view(),
        name="password_reset",
    ),

    path(
        "reset/done/",
        views.PasswordResetDoneView.as_view(
            template_name=(
                "registration/"
                "password_reset_done.html"
            ),
        ),
        name="password_reset_done",
    ),

    path(
        "reset/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(
            template_name=(
                "registration/"
                "password_reset_confirm.html"
            ),
        ),
        name="password_reset_confirm",
    ),

    path(
        "reset/complete/",
        views.PasswordResetCompleteView.as_view(
            template_name=(
                "registration/"
                "password_reset_complete.html"
            ),
        ),
        name="password_reset_complete",
    ),
]