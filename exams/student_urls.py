from django.urls import path

from . import student_views


app_name = "exams_student"


urlpatterns = [

    path(
        "",
        student_views.student_exam_home,
        name="home",
    ),

    path(
        "<int:pk>/preview/",
        student_views.student_exam_preview,
        name="preview",
    ),

    path(
        "<int:pk>/start/",
        student_views.student_exam_start,
        name="start",
    ),

    path(
        "attempt/<int:attempt_id>/",
        student_views.student_exam_take,
        name="take",
    ),

    path(
        (
            "attempt/"
            "<int:attempt_id>/"
            "answer/"
            "<int:exam_question_id>/"
        ),
        student_views.student_save_answer,
        name="save_answer",
    ),


    path(
        (
            "attempt/"
            "<int:attempt_id>/"
            "flag/"
            "<int:exam_question_id>/"
        ),
        student_views.student_save_flag,
        name="save_flag",
    ),

    path(
        (
            "attempt/"
            "<int:attempt_id>/"
            "event/"
        ),
        student_views.student_event_log,
        name="event_log",
    ),

    path(
        (
            "attempt/"
            "<int:attempt_id>/"
            "submit/"
        ),
        student_views.student_exam_submit,
        name="submit",
    ),

    path(
        (
            "attempt/"
            "<int:attempt_id>/"
            "result/"
        ),
        student_views.student_exam_result,
        name="result",
    ),
]