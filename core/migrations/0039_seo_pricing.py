"""Client SEO content: Section 07 Transparent Cab Fares (same wording as seed_content)."""
from django.db import migrations, models

from core.seo_content import PRICING_PLANS_SEO, PRICING_SEO


def apply_content(apps, schema_editor):
    apps.get_model("core", "PricingSection").objects.filter(pk=1).update(**PRICING_SEO)
    PricingPlan = apps.get_model("core", "PricingPlan")
    for car_name, data in PRICING_PLANS_SEO.items():
        PricingPlan.objects.filter(car__name=car_name).update(**data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_seo_safety'),
    ]

    operations = [
        migrations.AddField(
            model_name='pricingplan',
            name='description',
            field=models.CharField(blank=True, help_text='Shown under the price. Leave empty to hide it.', max_length=250, verbose_name='Short description'),
        ),
        migrations.AddField(
            model_name='pricingplan',
            name='subtitle',
            field=models.CharField(blank=True, help_text='e.g. Affordable Sedan Cab. Leave empty to hide it.', max_length=60, verbose_name='Line under plan name'),
        ),
        migrations.AddField(
            model_name='pricingsection',
            name='highlights',
            field=models.TextField(blank=True, help_text='Write one point per line, e.g. No Hidden Charges. Leave empty to hide them.', verbose_name='Green points under the paragraph'),
        ),
        migrations.AlterField(
            model_name='pricingsection',
            name='description',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **cab booking**', verbose_name='Short paragraph'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
