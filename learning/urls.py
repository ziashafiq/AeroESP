from django.urls import path

from . import views


app_name = "learning"


urlpatterns = [
    path(
        "",
        views.dashboard,
        name="dashboard",
    ),

    path(
        "courses/",
        views.my_courses,
        name="my_courses",
    ),

    path(
        "ielts/",
        views.ielts_dashboard,
        name="ielts_dashboard",
    ),

    path(
        "aerospace/",
        views.aerospace_dashboard,
        name="aerospace_dashboard",
    ),

    path(
        "courses/<int:pk>/",
        views.course_detail,
        name="course_detail",
    ),

    path(
        "modules/<int:module_id>/",
        views.module_detail,
        name="module_detail",
    ),

    path(
        "journal/",
        views.learning_journal,
        name="learning_journal",
    ),

    path(
        "journal/add/",
        views.learning_item_create,
        name="learning_item_create",
    ),

    path(
        "review/",
        views.review_due,
        name="review_due",
    ),

    path(
        "errors/",
        views.my_errors,
        name="my_errors",
    ),
]