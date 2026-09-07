from django.urls import path

from . import help_views


urlpatterns = [

    path(
        "",
        help_views.help_list,
        name="help_list",
    ),

    path(
        "mine/",
        help_views.help_for_me,
        name="help_for_me",
    ),

    path(
        "<slug:slug>/",
        help_views.help_detail,
        name="help_detail",
    ),

]
