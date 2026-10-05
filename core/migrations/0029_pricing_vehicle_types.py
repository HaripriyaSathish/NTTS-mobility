"""Pricing plans for the client's 5 vehicle types (existing plans renamed in place, Premium SUV added)."""
from django.db import migrations

from core.pricing_content import PRICING_PLANS


def apply_plans(apps, schema_editor):
    PricingPlan = apps.get_model("core", "PricingPlan")
    VehicleClass = apps.get_model("core", "VehicleClass")

    for data in PRICING_PLANS:
        values = {k: v for k, v in data.items() if k != "old_titles"}
        values["car"] = VehicleClass.objects.filter(name=data["car"]).first()
        if values["car"] is None:
            continue  # car missing (fresh database): seed_content creates the plan later
        plan = None
        for title in [data["title"], *data["old_titles"]]:
            plan = PricingPlan.objects.filter(title=title).first()
            if plan:
                break
        if plan is None:
            PricingPlan.objects.create(price_suffix="/ base fare", **values)
        else:
            PricingPlan.objects.filter(pk=plan.pk).update(**values)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0028_client_vehicle_types"),
    ]

    operations = [
        migrations.RunPython(apply_plans, migrations.RunPython.noop),
    ]
