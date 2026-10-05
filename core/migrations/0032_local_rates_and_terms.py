"""Local – Hourly Rentals: the client's real rates (ONLINE RATE 26-27), 5 packages and terms & conditions."""
from django.db import migrations, models

from core.booking_content import LOCAL_TERMS, RENTAL_PACKAGES, rate_rows


def apply_content(apps, schema_editor):
    BookingModal = apps.get_model("core", "BookingModal")
    VehicleClass = apps.get_model("core", "VehicleClass")
    RentalPackage = apps.get_model("core", "RentalPackage")
    TripRate = apps.get_model("core", "TripRate")

    BookingModal.objects.filter(pk=1).update(local_terms=LOCAL_TERMS)

    # Add the new packages (6 Hrs, 10 Hrs) and put all 5 in hour order
    packages = {}
    for order, name in enumerate(RENTAL_PACKAGES, start=1):
        package, _ = RentalPackage.objects.get_or_create(name=name, defaults={"order": order})
        RentalPackage.objects.filter(pk=package.pk).update(order=order)
        packages[name] = package

    # The old Local prices were samples, so they are replaced with the real rates
    for car in VehicleClass.objects.all():
        for row in rate_rows(car.name):
            if row["trip_type"] != "local":
                continue
            package = packages[row.pop("package")]
            TripRate.objects.update_or_create(vehicle=car, trip_type=row.pop("trip_type"), package=package,
                                              defaults=row)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_booking_trip_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookingmodal',
            name='local_terms',
            field=models.TextField(blank=True, help_text='Shown under the packages on the Local – Hourly Rentals tab. One point per line. Leave empty to hide it.', verbose_name='Local – terms & conditions'),
        ),
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
