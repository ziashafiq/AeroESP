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


def canonical_url(request):
    """
    The <link rel="canonical"> target for the current path.

    Built from AEROESP_CANONICAL_HOST rather than request.get_host(),
    so it names the eventual domain even for a request that arrives on
    the platform's default host or www - both of which
    CanonicalDomainMiddleware redirects away before a page ever
    renders, but staying independent of the current host keeps this
    correct regardless of middleware ordering. None (and therefore no
    tag at all - see templates/aeroesp/public_base.html) until the
    custom domain is actually configured, since pointing "canonical"
    at a hostname visitors cannot yet reach would be worse than
    omitting the tag.

    Query strings are dropped: every public page here is a static
    destination, none of them paginate or filter through the URL.
    """

    canonical_host = settings.AEROESP_CANONICAL_HOST

    if not canonical_host:
        return {"CANONICAL_URL": None}

    return {
        "CANONICAL_URL": (
            f"https://{canonical_host}{request.path}"
        ),
    }


def color_palette(request):
    """
    The palette to stamp on <html> before the first paint.

    Rendered server-side for signed-in users so their choice follows
    them to any device with no flash of the default blue. Anonymous
    visitors get None here and the inline bootstrap fills it in from
    localStorage instead.
    """

    user = getattr(request, "user", None)

    if user is None or not user.is_authenticated:
        return {"USER_PALETTE": None}

    return {
        "USER_PALETTE": (
            getattr(user, "color_palette", None) or "skyline"
        ),
    }
