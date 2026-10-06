"""Client SEO content: Section 08 Rider Experiences heading (same wording as seed_content)."""
from django.db import migrations, models

from core.seo_content import TESTIMONIALS_SECTION_SEO


def apply_content(apps, schema_editor):
    apps.get_model("core", "TestimonialsSection").objects.filter(pk=1).update(**TESTIMONIALS_SECTION_SEO)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_seo_pricing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testimonialssection',
            name='description',
            field=models.TextField(help_text='To make words bold, put two stars on each side: **reliable cab booking**', verbose_name='Paragraph on the right'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
