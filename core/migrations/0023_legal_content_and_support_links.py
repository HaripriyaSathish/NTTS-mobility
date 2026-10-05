"""
Add the Privacy Policy / Terms of Transit popups and point the footer Support & Legal
links at sections on the page (the Legal links open the popups).
"""
from django.db import migrations

from core.legal_content import LEGAL_LINKS, LEGAL_PAGES, SUPPORT_LINKS


def apply_changes(apps, schema_editor):
    LegalPage = apps.get_model("core", "LegalPage")
    FooterColumn = apps.get_model("core", "FooterColumn")
    FooterLink = apps.get_model("core", "FooterLink")

    for data in LEGAL_PAGES:
        if not LegalPage.objects.filter(slug=data["slug"]).exists():
            LegalPage.objects.create(**data)

    for title, links in (("SUPPORT", SUPPORT_LINKS), ("LEGAL", LEGAL_LINKS)):
        column = FooterColumn.objects.filter(title__iexact=title).first()
        if column is None:
            continue
        FooterLink.objects.filter(column=column).delete()
        for i, (label, link) in enumerate(links, start=1):
            FooterLink.objects.create(column=column, label=label, link=link, order=i)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0022_legal_popups"),
    ]

    operations = [
        migrations.RunPython(apply_changes, migrations.RunPython.noop),
    ]
