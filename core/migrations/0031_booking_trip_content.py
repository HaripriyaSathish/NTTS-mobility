"""Booking popup trip tabs: wording, car seats, Local packages and (sample) prices per car."""
from django.db import migrations

from core.booking_content import BOOKING_TEXT, RENTAL_PACKAGES, SEATS, rate_rows


def apply_content(apps, schema_editor):
    BookingModal = apps.get_model("core", "BookingModal")
    VehicleClass = apps.get_model("core", "VehicleClass")
    RentalPackage = apps.get_model("core", "RentalPackage")
    TripRate = apps.get_model("core", "TripRate")

    BookingModal.objects.filter(pk=1).update(**BOOKING_TEXT)

    for name, seats in SEATS.items():
        VehicleClass.objects.filter(name=name).update(seats=seats)

    packages = {}
    for order, name in enumerate(RENTAL_PACKAGES, start=1):
        packages[name], _ = RentalPackage.objects.get_or_create(name=name, defaults={"order": order})

    # Only add prices that are missing, so prices already changed in admin are kept
    for car in VehicleClass.objects.all():
        for row in rate_rows(car.name):
            package = packages.get(row.pop("package"))
            TripRate.objects.get_or_create(vehicle=car, trip_type=row.pop("trip_type"), package=package, defaults=row)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0030_booking_trip_tabs"),
    ]

    operations = [
        migrations.RunPython(apply_content, migrations.RunPython.noop),
    ]
