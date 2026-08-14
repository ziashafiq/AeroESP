from django.urls import path

from . import views


app_name = "exams"


urlpatterns = [

    path(
        "",
        views.teacher_exam_list,
        name="teacher_exam_list",
    ),

    path(
        "create/",
        views.teacher_exam_create,
        name="teacher_exam_create",
    ),

    path(
        "<int:pk>/",
        views.teacher_exam_detail,
        name="teacher_exam_detail",
    ),

    path(
        "<int:pk>/edit/",
        views.teacher_exam_edit,
        name="teacher_exam_edit",
    ),

    path(
        "<int:pk>/questions/",
        views.teacher_exam_question_bank,
        name="teacher_exam_question_bank",
    ),

    path(
        "<int:pk>/structure/",
        views.teacher_exam_structure,
        name="teacher_exam_structure",
    ),

    path(
        "<int:pk>/publish/",
        views.teacher_exam_publish,
        name="teacher_exam_publish",
    ),
]