from django.urls import path

from . import teacher_views


app_name = "teacher_questions"


urlpatterns = [

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
]