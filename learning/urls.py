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
        "resources/",
        views.resource_list,
        name="resource_list",
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

    path(
        "errors/<int:error_id>/resolve/",
        views.resolve_learner_error,
        name="resolve_learner_error",
    ),

    path(
        "items/<int:learning_item_id>/question/add/",
        views.create_practice_question,
        name="learning_question_create",
    ),

    path(
        "api/aerospace-topics/",
        views.aerospace_topics_api,
        name="aerospace_topics_api",
    ),

    path(
        "modules/<int:module_id>/topics/<int:topic_id>/",
        views.aerospace_topic_detail,
        name="aerospace_topic_detail",
    ),

    path(
        "practice/",
        views.daily_practice,
        name="daily_practice",
    ),

    path(
        "practice/<int:link_id>/answer/",
        views.practice_answer,
        name="practice_answer",
    ),

    path(
        "placement/",
        views.placement_test,
        name="placement_test",
    ),

    path(
        "placement/result/<int:attempt_id>/",
        views.placement_result,
        name="placement_result",
    ),

    path(
        "path/",
        views.learning_path,
        name="learning_path",
    ),

    path(
        "analytics/",
        views.learning_analytics,
        name="learning_analytics",
    ),

    path(
        "teacher/",
        views.teacher_learning_dashboard,
        name="teacher_learning_dashboard",
    ),

    path(
        "teacher/courses/<int:course_id>/class/",
        views.teacher_class_detail,
        name="teacher_class_detail",
    ),

    path(
        "teacher/students/<int:student_id>/",
        views.teacher_student_detail,
        name="teacher_student_detail",
    ),

    path(
        "teacher/resources/add/",
        views.teacher_resource_create,
        name="teacher_resource_create",
    ),

    path(
        "teacher/resources/",
        views.teacher_resource_list,
        name="teacher_resource_list",
    ),
]