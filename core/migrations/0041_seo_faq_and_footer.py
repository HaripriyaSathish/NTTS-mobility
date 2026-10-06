"""Client SEO content: Section 10 FAQ + Section 11 Footer (same wording as seed_content)."""
from django.db import migrations, models

from core.seo_content import FAQ_ITEMS_SEO, FOOTER_SEO


def apply_content(apps, schema_editor):
    FAQItem = apps.get_model("core", "FAQItem")
    questions = [question for question, _ in FAQ_ITEMS_SEO]
    # The earlier questions are hidden (not deleted) and moved after the new ones
    for i, item in enumerate(FAQItem.objects.exclude(question__in=questions).order_by("order", "id"), start=101):
        FAQItem.objects.filter(pk=item.pk).update(is_active=False, order=i)
    for order, (question, answer) in enumerate(FAQ_ITEMS_SEO, start=1):
        FAQItem.objects.update_or_create(question=question,
                                         defaults={"answer": answer, "order": order, "is_active": True})

    apps.get_model("core", "FooterSettings").objects.filter(pk=1).update(**FOOTER_SEO)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_seo_rider_experiences'),
    ]

    operations = [
        migrations.AddField(
            model_name='footersettings',
            name='highlights',
            field=models.TextField(blank=True, help_text='Write one point per line, e.g. Safe Rides. Leave empty to hide them.', verbose_name='Green points under the text'),
        ),
        migrations.AddField(
            model_name='footersettings',
            name='tagline',
            field=models.CharField(blank=True, help_text='e.g. Safe & Reliable Mobility for the Modern City. Leave empty to hide it.', max_length=80, verbose_name='Heading under the logo'),
        ),
        migrations.AlterField(
            model_name='footersettings',
            name='about_text',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **online cab booking**', verbose_name='Text under the logo'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
