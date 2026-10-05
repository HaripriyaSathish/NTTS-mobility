from django.conf import settings
from django.db.models import Prefetch

from .models import FooterColumn, FooterLink, FooterSettings, SiteSettings


def asset_version():
    """Changes whenever style.css or main.js is edited, so browsers never keep an old copy."""
    folder = settings.BASE_DIR / "static"
    try:
        return int(max((folder / "css/style.css").stat().st_mtime, (folder / "js/main.js").stat().st_mtime))
    except OSError:
        return 1


def site_settings(request):
    site = SiteSettings.load()
    footer = FooterSettings.load()
    return {
        "asset_version": asset_version(),
        "site": site,
        "nav_items": site.nav_items.filter(is_active=True) if site else [],
        "footer": footer,
        "social_links": footer.social_links.filter(is_active=True) if footer else [],
        "footer_columns": FooterColumn.objects.filter(is_active=True).prefetch_related(
            Prefetch("links", queryset=FooterLink.objects.filter(is_active=True), to_attr="active_links")
        ),
    }
