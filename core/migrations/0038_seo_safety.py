"""Client SEO content: Section 06 Safety (same wording as seed_content). No ISO tag, card 6 hidden."""
from django.db import migrations, models

from core.seo_content import SAFETY_FEATURES_SEO, SAFETY_SEO


def apply_content(apps, schema_editor):
    apps.get_model("core", "SafetySection").objects.filter(pk=1).update(**SAFETY_SEO)
    SafetyFeature = apps.get_model("core", "SafetyFeature")
    cards = list(SafetyFeature.objects.order_by("order", "id"))
    for position, data in SAFETY_FEATURES_SEO.items():
        if position <= len(cards):
            SafetyFeature.objects.filter(pk=cards[position - 1].pk).update(**data)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_seo_how_it_works'),
    ]

    operations = [
        migrations.AddField(
            model_name='safetyfeature',
            name='check_text',
            field=models.CharField(blank=True, help_text='e.g. Verified Driver Screening (the ✓ is added for you). Leave empty to hide it.', max_length=80, verbose_name='Green tick line at bottom'),
        ),
        migrations.AddField(
            model_name='safetyfeature',
            name='subtitle',
            field=models.CharField(blank=True, help_text='e.g. Trusted Drivers for Every Journey. Leave empty to hide it.', max_length=80, verbose_name='Line under heading'),
        ),
        migrations.AddField(
            model_name='safetysection',
            name='highlight_tag',
            field=models.CharField(blank=True, help_text='e.g. 24/7 Ride Monitoring. Leave empty to hide it.', max_length=60, verbose_name='Highlight box – green line at bottom'),
        ),
        migrations.AlterField(
            model_name='safetysection',
            name='description',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **online cab booking**', verbose_name='Short paragraph'),
        ),
        migrations.AlterField(
            model_name='safetysection',
            name='highlight_text',
            field=models.CharField(blank=True, help_text='To make words bold, put two stars on each side: **taxi booking**', max_length=400, verbose_name='Highlight box – text'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
