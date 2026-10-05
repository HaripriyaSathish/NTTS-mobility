"""
Client changes for the New Track rebrand, applied to the existing content so the live
site updates on `migrate` (the same wording is also in seed_content).
"""
from django.db import migrations

NAV_ITEMS = [
    ("Home", "#home"),
    ("About Us", "#about"),
    ("Fleet & Rides", "#fleet"),
    ("How It Works", "#how-it-works"),
    ("Safety", "#safety"),
    ("Pricing", "#pricing"),
]

ABOUT = {
    "is_active": True,
    "badge_text": "ABOUT US",
    "title": "Driven by Trust, Built for Every Journey",
    "description": (
        "New Track by NTTS Car Rentals is a Chennai-based cab and car rental service built on one idea: "
        "your destination is our vision. From daily city rides to airport transfers and outstation trips, "
        "we get you there safely, on time, and at a fair, upfront price.\n"
        "Every ride is handled by verified, experienced drivers in clean, well-maintained cars, backed by a "
        "help desk that is always a call away."
    ),
    "image_alt": "New Track car rental fleet",
    "mission_title": "Our Mission",
    "mission_text": "To make every ride safe, punctual and fairly priced, with verified drivers, clean cars and no hidden charges.",
    "vision_title": "Our Vision",
    "vision_text": "Your destination, our vision: to be the most trusted travel partner for every journey we are part of.",
}


def apply_changes(apps, schema_editor):
    get = lambda name: apps.get_model("core", name)

    site = get("SiteSettings").objects.filter(pk=1).first()
    if site:
        site.site_name = "New Track"
        site.logo_alt = "New Track"
        site.meta_title = "New Track | Your Destination – Our Vision"
        site.og_title = "New Track | Your Destination – Our Vision"
        site.save()
        # Add "About Us" to the menu, right after Home
        NavItem = get("NavItem")
        if not NavItem.objects.filter(site=site, link="#about").exists():
            for i, (label, link) in enumerate(NAV_ITEMS, start=1):
                item = NavItem.objects.filter(site=site, link=link).first()
                if item:
                    item.order = i
                    item.save(update_fields=["order"])
                else:
                    NavItem.objects.create(site=site, label=label, link=link, order=i)

    get("HeroSection").objects.filter(pk=1).update(
        title="Your Destination —", title_highlight="Our Vision",
        eta_text="Avg ETA 30 mins", pickup_label="Pickup City",
    )
    get("BookingModal").objects.filter(pk=1).update(
        pickup_label="Pickup City", departing_highlight="Within 30–40 Mins",
        departing_note="", button_prefix="Book",
    )
    # No "POPULAR" tag and no car pre-selected (that was the green border)
    VehicleClass = get("VehicleClass")
    VehicleClass.objects.filter(badge_text__iexact="POPULAR").update(badge_text="")
    VehicleClass.objects.update(is_default=False)

    get("SafetySection").objects.filter(pk=1, badge_text="ISO 27001 CERTIFIED SAFETY").update(badge_text="")

    get("FooterSettings").objects.filter(pk=1).update(copyright_text="© {year} NTTS CAR RENTALS. All rights reserved.")

    # Footer "COMPANY" column = the navbar sections (instead of Careers / Press / Blog)
    FooterColumn, FooterLink = get("FooterColumn"), get("FooterLink")
    company = FooterColumn.objects.filter(title__iexact="COMPANY").first()
    if company:
        FooterLink.objects.filter(column=company).delete()
        for i, (label, link) in enumerate(NAV_ITEMS, start=1):
            FooterLink.objects.create(column=company, label=label, link=link, order=i)

    AboutSection = get("AboutSection")
    if not AboutSection.objects.filter(pk=1).exists():
        AboutSection.objects.create(pk=1, **ABOUT)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0017_about_section_and_optional_tags"),
    ]

    operations = [
        migrations.RunPython(apply_changes, migrations.RunPython.noop),
    ]
