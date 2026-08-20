from django.urls import path

from . import views


app_name = "intelligence"


urlpatterns = [

    path(
        "",
        views.ai_dashboard,
        name="dashboard",
    ),

    path(
        "questions/<int:question_id>/analyze/",
        views.analyze_question_view,
        name="analyze_question",
    ),

    path(
        "suggestions/<int:suggestion_id>/",
        views.suggestion_detail,
        name="suggestion_detail",
    ),

    path(
        "suggestions/<int:suggestion_id>/<str:decision>/",
        views.review_suggestion,
        name="review_suggestion",
    ),

    path(
        "students/<int:student_id>/insight/",
        views.learner_insight,
        name="learner_insight",
    ),
]