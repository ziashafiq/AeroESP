from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from accounts.models import HelpGuide


def _sitemap_domain():
    """
    The domain django.contrib.sitemaps stamps into every <loc>.

    Deliberately not django.contrib.sites (no Sites framework is
    installed - it would need its own migration and SITE_ID just for
    this one value). Falls back to the Liara host so sitemap.xml is
    still valid before the custom domain's DNS/SSL is ready; once
    AEROESP_CANONICAL_HOST is set, every URL points at the domain
    search engines are meant to index, matching the <link
    rel="canonical"> tag (accounts.context_processors.canonical_url).
    """

    return (
        settings.AEROESP_CANONICAL_HOST
        or (settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else "")
    )


class StaticViewSitemap(Sitemap):
    """
    Every public, login-free page that is not a form or an
    account-management action (register/login/reset are excluded on
    purpose - see robots.txt: nothing is gained by indexing them, and
    a search result landing mid-flow is a poor experience).
    """

    protocol = "https"

    changefreq = "monthly"

    priority = 0.7

    def items(self):

        return [
            "home",
            "terms",
            "quiz",
            "help_list",
            "research_review:getting_started",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        # The landing page is what most inbound links and search
        # results should prefer over the others.
        return 1.0 if item == "home" else 0.7

    def get_domain(self, site=None):
        """
        Sitemap.get_domain() normally falls back to
        django.contrib.sites (Site.objects.get_current()), which
        needs its own migration and SITE_ID just for one string.
        Answering directly makes that app unnecessary here.
        """

        return _sitemap_domain()


class HelpGuideSitemap(Sitemap):
    """
    Individual guide pages - dynamic, so they need their own last-
    modified date rather than the whole sitemap sharing one.
    """

    protocol = "https"

    changefreq = "monthly"

    priority = 0.5

    def items(self):

        return HelpGuide.objects.filter(
            is_published=True,
        )

    def location(self, guide):
        return guide.get_absolute_url()

    def lastmod(self, guide):
        return guide.updated_at

    def get_domain(self, site=None):
        return _sitemap_domain()


sitemaps = {
    "static": StaticViewSitemap,
    "guides": HelpGuideSitemap,
}
