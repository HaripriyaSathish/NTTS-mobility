from django.db.models import Prefetch

from .models import FooterColumn, FooterLink, FooterSettings, SiteSettings


def site_settings(request):
    site = SiteSettings.load()
    footer = FooterSettings.load()
    return {
        "site": site,
        "nav_items": site.nav_items.filter(is_active=True) if site else [],
        "footer": footer,
        "social_links": footer.social_links.filter(is_active=True) if footer else [],
        "footer_columns": FooterColumn.objects.filter(is_active=True).prefetch_related(
            Prefetch("links", queryset=FooterLink.objects.filter(is_active=True), to_attr="active_links")
        ),
    }
