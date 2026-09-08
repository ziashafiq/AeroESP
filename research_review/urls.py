from django.urls import path

from . import views


app_name = "research_review"


urlpatterns = [

    path(
        "getting-started/",
        views.getting_started,
        name="getting_started",
    ),

    path(
        "",
        views.reviewer_dashboard,
        name="dashboard",
    ),

    path(
        "item/<int:assignment_id>/",
        views.review_item,
        name="review_item",
    ),

    # Staff only. Reviewers must not see how the panel is scoring
    # while they are still scoring - see the view for why.
    path(
        "analysis/",
        views.analysis,
        name="analysis",
    ),

]
