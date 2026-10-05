"""Fill About Us with the client's real wording: founder story, services, mission/vision/why and values."""
from django.db import migrations

from core.about_content import ABOUT, ABOUT_VALUES


def use_client_content(apps, schema_editor):
    AboutSection = apps.get_model("core", "AboutSection")
    AboutValue = apps.get_model("core", "AboutValue")

    about = AboutSection.objects.filter(pk=1).first()
    if about is None:
        about = AboutSection.objects.create(pk=1, **ABOUT)
    else:
        for key, value in ABOUT.items():
            if key != "is_active":  # keep the show/hide choice made in admin
                setattr(about, key, value)
        about.save()

    if not AboutValue.objects.filter(section=about).exists():
        for data in ABOUT_VALUES:
            AboutValue.objects.create(section=about, **data)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0026_about_services_values"),
    ]

    operations = [
        migrations.RunPython(use_client_content, migrations.RunPython.noop),
    ]
