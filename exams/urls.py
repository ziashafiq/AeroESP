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
        "integrity/",
        views.teacher_integrity_dashboard,
        name="teacher_integrity_dashboard",
    ),

    path(
        "<int:pk>/integrity/",
        views.teacher_exam_integrity,
        name="teacher_exam_integrity",
    ),

    path(
        "<int:pk>/integrity/export/",
        views.teacher_exam_integrity_export,
        name="teacher_exam_integrity_export",
    ),

    path(
        (
            "<int:pk>/attempts/"
            "<int:attempt_id>/integrity/"
        ),
        views.teacher_attempt_integrity,
        name="teacher_attempt_integrity",
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