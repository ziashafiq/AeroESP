from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalDomainMiddleware:
    """
    301-redirects the platform's default host and the www subdomain to
    the canonical apex domain, in a single hop.

    Placed ahead of SecurityMiddleware in MIDDLEWARE on purpose: this
    redirect always targets an explicit https:// URL, so a plain-HTTP
    request to the old host lands on the canonical domain directly
    instead of SecurityMiddleware first redirecting HTTP -> HTTPS on
    the OLD host and this middleware then redirecting a second time.

    A no-op wherever AEROESP_CANONICAL_HOST is unset - local
    development, or any deploy that has not been given a custom domain
    yet - so it changes nothing until that variable is set.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        canonical_host = settings.AEROESP_CANONICAL_HOST

        if canonical_host:

            # get_host() also strips a forwarded port; done manually
            # here since that call raises DisallowedHost for a host
            # not in ALLOWED_HOSTS, which is exactly the case for a
            # request that has not been redirected yet.
            host = (
                request.META.get("HTTP_HOST", "")
                .split(":")[0]
                .lower()
            )

            is_www_of_canonical = (
                host == f"www.{canonical_host}"
            )

            is_legacy_host = (
                host in settings.AEROESP_LEGACY_HOSTS
            )

            if (
                host
                and host != canonical_host
                and (is_www_of_canonical or is_legacy_host)
            ):

                return HttpResponsePermanentRedirect(
                    f"https://{canonical_host}"
                    f"{request.get_full_path()}"
                )

        return self.get_response(request)
