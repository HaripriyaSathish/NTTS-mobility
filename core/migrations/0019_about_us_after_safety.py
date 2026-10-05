"""Move "About Us" after "Safety" in the menu and the footer Company column (matches the page order)."""
from django.db import migrations

ORDER = ["#home", "#fleet", "#how-it-works", "#safety", "#about", "#pricing"]


def reorder(apps, schema_editor):
    NavItem = apps.get_model("core", "NavItem")
    FooterLink = apps.get_model("core", "FooterLink")
    for i, link in enumerate(ORDER, start=1):
        NavItem.objects.filter(link=link).update(order=i)
        FooterLink.objects.filter(column__title__iexact="COMPANY", link=link).update(order=i)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_client_changes_new_track"),
    ]

    operations = [
        migrations.RunPython(reorder, migrations.RunPython.noop),
    ]
