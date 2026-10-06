"""Client SEO content: Section 04 How It Works + Section 05 banner (same wording as seed_content)."""
from django.db import migrations, models

from core.seo_content import STEPS_SECTION_SEO, STEPS_SEO


def apply_content(apps, schema_editor):
    apps.get_model("core", "StepsSection").objects.filter(pk=1).update(**STEPS_SECTION_SEO)
    Step = apps.get_model("core", "Step")
    steps = list(Step.objects.order_by("order", "id"))
    for position, data in STEPS_SEO.items():
        if position <= len(steps):
            Step.objects.filter(pk=steps[position - 1].pk).update(**data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0036_seo_fleet_and_rides'),
    ]

    operations = [
        migrations.AlterField(
            model_name='step',
            name='description',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **cab fare**', verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='step',
            name='highlight_text',
            field=models.CharField(blank=True, help_text='e.g. **Live Ride Tracking –** Stay updated on your driver. Words between ** show in bold green. Leave empty to hide.', max_length=200, verbose_name='Highlight line at bottom'),
        ),
        migrations.AlterField(
            model_name='stepssection',
            name='banner_text',
            field=models.CharField(blank=True, help_text='To make words bold, put two stars on each side: **cab for city travel**', max_length=300, verbose_name='Banner text'),
        ),
        migrations.AlterField(
            model_name='stepssection',
            name='description',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **cab or taxi online**', verbose_name='Short paragraph'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
