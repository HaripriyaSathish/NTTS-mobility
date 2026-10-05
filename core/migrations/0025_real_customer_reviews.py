"""Replace the sample testimonials with the client's real customer reviews."""
from django.db import migrations

from core.reviews_content import TESTIMONIALS, TESTIMONIALS_SECTION_DESCRIPTION

SAMPLE_NAMES = ["Priya Sharma", "Marcus Vance", "Dr. Ananya Roy"]


def use_real_reviews(apps, schema_editor):
    Testimonial = apps.get_model("core", "Testimonial")
    TestimonialsSection = apps.get_model("core", "TestimonialsSection")

    Testimonial.objects.filter(name__in=SAMPLE_NAMES).delete()
    for data in TESTIMONIALS:
        if not Testimonial.objects.filter(name=data["name"]).exists():
            Testimonial.objects.create(**data)

    TestimonialsSection.objects.filter(pk=1, description__contains="NTTS Mobility").update(
        description=TESTIMONIALS_SECTION_DESCRIPTION
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0024_testimonial_role_optional"),
    ]

    operations = [
        migrations.RunPython(use_real_reviews, migrations.RunPython.noop),
    ]
