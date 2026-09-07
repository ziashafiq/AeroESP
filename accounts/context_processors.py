from django.conf import settings


def support_email(request):
    """
    Makes the support address available to every template - the
    footer and sidebar "report a problem" links need it on every page,
    not just the few views that already built their own context.
    """

    return {
        "AEROESP_SUPPORT_EMAIL": settings.AEROESP_SUPPORT_EMAIL,
    }
