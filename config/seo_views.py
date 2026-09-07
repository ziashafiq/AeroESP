from django.http import HttpResponse


ROBOTS_TXT = """\
User-agent: *

Allow: /$
Allow: /terms/
Allow: /help/
Allow: /quiz/
Allow: /expert-review/getting-started/
Allow: /sitemap.xml

Disallow: /admin/
Disallow: /accounts/
Disallow: /learn/
Disallow: /teacher/
Disallow: /student/
Disallow: /ai/
Disallow: /captcha/
Disallow: /expert-review/

Sitemap: {sitemap_url}
"""


def robots_txt(request):
    """
    Everything requiring a login is disallowed wholesale by
    section (/accounts/, /learn/, /teacher/, /student/, /ai/,
    /expert-review/), with the handful of public pages living under
    those same crawl roots (notably /expert-review/getting-started/)
    allowed individually. Per the robots.txt spec, the longest -
    i.e. most specific - matching rule wins regardless of the order
    rules appear in, so an Allow line does not need to precede the
    Disallow it overrides.
    """

    sitemap_url = request.build_absolute_uri("/sitemap.xml")

    return HttpResponse(
        ROBOTS_TXT.format(sitemap_url=sitemap_url),
        content_type="text/plain",
    )
