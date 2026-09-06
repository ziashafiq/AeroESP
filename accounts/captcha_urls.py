from django.urls import path

from . import captcha_views


urlpatterns = [

    path(
        "image/<str:key>/",
        captcha_views.captcha_image,
        name="captcha_image",
    ),

    path(
        "new/",
        captcha_views.captcha_refresh,
        name="captcha_refresh",
    ),

]
