"""Client rates (ONLINE RATE 26-27, "Local" sheet): the base price on the booking popup cars,
Fleet & Rides cards and Pricing plans becomes the 4 Hrs / 40 Km package price, and the
per-km lines / FAQ answer use the sheet's extra Km and extra hour rates."""
from django.db import migrations

from core.booking_content import starting_price
from core.seo_content import FAQ_ITEMS_SEO, PRICING_PLANS_SEO

FAQ_QUESTION = "How much does a New Track cab cost, and is there surge pricing?"


def apply_prices(apps, schema_editor):
    VehicleClass = apps.get_model("core", "VehicleClass")
    RideOption = apps.get_model("core", "RideOption")
    PricingPlan = apps.get_model("core", "PricingPlan")
    FAQItem = apps.get_model("core", "FAQItem")

    for car in VehicleClass.objects.all():
        try:
            price = starting_price(car.name)
        except KeyError:
            continue
        VehicleClass.objects.filter(pk=car.pk).update(base_price=price)
        RideOption.objects.filter(booking_car=car).update(base_price=price)
        texts = PRICING_PLANS_SEO.get(car.name)
        if texts:
            PricingPlan.objects.filter(car=car).update(features=texts["features"])

    answer = dict(FAQ_ITEMS_SEO).get(FAQ_QUESTION)
    if answer:
        FAQItem.objects.filter(question=FAQ_QUESTION).update(answer=answer)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_stat_link'),
    ]

    operations = [
        migrations.RunPython(apply_prices, migrations.RunPython.noop),
    ]
