"""Client SEO content: stats row labels (same wording as seed_content)."""
from django.db import migrations

from core.seo_content import STATS_SEO


def apply_content(apps, schema_editor):
    StatItem = apps.get_model("core", "StatItem")
    for number, label in STATS_SEO.items():
        StatItem.objects.filter(number=number).update(label=label)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_seo_featured_vehicles'),
    ]

    operations = [
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
