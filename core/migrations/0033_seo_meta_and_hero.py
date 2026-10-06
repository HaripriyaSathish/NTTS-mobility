"""Client SEO content: Meta Tags + Section 01 Hero (same wording as seed_content)."""
from django.db import migrations, models

from core.seo_content import HERO_SEO, SITE_SEO


def apply_content(apps, schema_editor):
    apps.get_model("core", "SiteSettings").objects.filter(pk=1).update(**SITE_SEO)
    apps.get_model("core", "HeroSection").objects.filter(pk=1).update(**HERO_SEO)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0032_local_rates_and_terms'),
    ]

    operations = [
        migrations.AddField(
            model_name='herosection',
            name='tab_labels',
            field=models.TextField(blank=True, help_text='Write one tab name per line, e.g. Airport Cab. Leave empty to hide the tabs.', verbose_name='Trip tabs'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
