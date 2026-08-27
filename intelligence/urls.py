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

    path(
        "generate/",
        views.generate_question_view,
        name="generate_question",
    ),

    path(
        "generated/<int:draft_id>/",
        views.generated_draft_detail,
        name="generated_draft_detail",
    ),

    path(
        "generated/<int:draft_id>/edit/",
        views.edit_generated_draft,
        name="edit_generated_draft",
    ),

    path(
        "generated/<int:draft_id>/accept/",
        views.accept_generated_draft,
        name="accept_generated_draft",
    ),

    path(
        "generated/<int:draft_id>/reject/",
        views.reject_generated_draft,
        name="reject_generated_draft",
    ),

    path(
        "experiment/run/",
        views.run_ai_experiment,
        name="run_ai_experiment",
    ),

    path(
        "experiments/",
        views.experiment_history,
        name="experiment_history",
    ),

    path(
        "experiments/<int:experiment_id>/report/",
        views.experiment_report_view,
        name="experiment_report",
    ),

    path(
        "settings/providers/",
        views.provider_settings_view,
        name="provider_settings",
    ),
]