from django.urls import path

from . import teacher_views


app_name = "teacher_questions"


urlpatterns = [

    # =====================================================
    # Question Bank
    # =====================================================

    path(
        "questions/",
        teacher_views.teacher_question_list,
        name="list",
    ),

    path(
        "questions/new/",
        teacher_views.teacher_question_create,
        name="create",
    ),

    path(
        "questions/<int:pk>/edit/",
        teacher_views.teacher_question_edit,
        name="edit",
    ),

    # =====================================================
    # Topic Search API
    # =====================================================

    path(
        "topics/search/",
        teacher_views.teacher_topic_search,
        name="topic_search",
    ),

    # =====================================================
    # Topic Proposals
    # =====================================================

    path(
        "topics/proposals/",
        teacher_views.teacher_topic_proposal_list,
        name="topic_proposals",
    ),

    path(
        "topics/propose/",
        teacher_views.teacher_topic_proposal_create,
        name="topic_propose",
    ),
]