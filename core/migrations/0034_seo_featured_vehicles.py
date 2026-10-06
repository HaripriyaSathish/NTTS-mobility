"""Client SEO content: Section 02 Featured Vehicles (same wording as seed_content)."""
from django.db import migrations, models

from core.seo_content import FLEET_SLIDES_SEO


def apply_content(apps, schema_editor):
    FleetSlide = apps.get_model("core", "FleetSlide")
    FleetSpec = apps.get_model("core", "FleetSpec")
    for tab_label, data in FLEET_SLIDES_SEO.items():
        data = dict(data)
        specs = data.pop("specs")
        for slide in FleetSlide.objects.filter(tab_label=tab_label):
            FleetSlide.objects.filter(pk=slide.pk).update(**data)
            FleetSpec.objects.filter(slide=slide).delete()
            for i, (label, value) in enumerate(specs, start=1):
                FleetSpec.objects.create(slide=slide, label=label, value=value, order=i)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_seo_meta_and_hero'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fleetslide',
            name='description',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **AC sedan cabs**', verbose_name='Description'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
