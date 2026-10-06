"""Client SEO content: Section 03 Fleet & Rides (same wording as seed_content)."""
from django.db import migrations, models

from core.seo_content import RIDE_CARDS_SEO, RIDES_SEO


def apply_content(apps, schema_editor):
    apps.get_model("core", "RidesSection").objects.filter(pk=1).update(**RIDES_SEO)
    RideOption = apps.get_model("core", "RideOption")
    for name, data in RIDE_CARDS_SEO.items():
        RideOption.objects.filter(name=name).update(**data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_seo_stats'),
    ]

    operations = [
        migrations.AddField(
            model_name='rideoption',
            name='subtitle',
            field=models.CharField(blank=True, help_text='e.g. Affordable City & Daily Travel. Leave empty to hide it.', max_length=80, verbose_name='Line under car type'),
        ),
        migrations.AlterField(
            model_name='ridessection',
            name='description',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **cab booking**', verbose_name='Short paragraph'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
