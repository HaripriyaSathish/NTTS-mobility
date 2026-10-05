"""
Client's 5 vehicle types in the booking popup and the Fleet & Rides cards.
Existing records are renamed in place, so uploaded photos and linked pricing plans are kept.
"""
from django.db import migrations

from core.vehicles_content import HIDDEN_RIDE_CARDS, RIDE_OPTIONS, VEHICLES


def find(model, data):
    for name in [data["name"], *data["old_names"]]:
        obj = model.objects.filter(name=name).first()
        if obj:
            return obj
    return None


def apply_vehicle_types(apps, schema_editor):
    VehicleClass = apps.get_model("core", "VehicleClass")
    RideOption = apps.get_model("core", "RideOption")

    for data in VEHICLES:
        values = {k: v for k, v in data.items() if k != "old_names"}
        car = find(VehicleClass, data)
        if car is None:
            VehicleClass.objects.create(**values)
        else:
            VehicleClass.objects.filter(pk=car.pk).update(**values)

    for data in RIDE_OPTIONS:
        values = {k: v for k, v in data.items() if k != "old_names"}
        values["booking_car"] = VehicleClass.objects.filter(name=data["booking_car"]).first()
        values["image_alt"] = data["name"]
        card = find(RideOption, data)
        if card is None:
            RideOption.objects.create(currency_symbol="₹", price_suffix="base", **values)
        else:
            RideOption.objects.filter(pk=card.pk).update(**values)

    RideOption.objects.filter(name__in=HIDDEN_RIDE_CARDS).update(is_active=False, booking_car=None)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0027_about_client_content"),
    ]

    operations = [
        migrations.RunPython(apply_vehicle_types, migrations.RunPython.noop),
    ]
