"""
Seed the landing page content with the wording from the design.

    python manage.py seed_content           # only fills what is missing
    python manage.py seed_content --reset   # overwrite text back to the design wording

Images are never touched; upload them in the admin panel.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.about_content import ABOUT, ABOUT_VALUES
from core.booking_content import BOOKING_TEXT, CHENNAI_LOCATIONS, LOCAL_TERMS, RENTAL_PACKAGES, SEATS, rate_rows
from core.pricing_content import PRICING_PLANS
from core.vehicles_content import RIDE_OPTIONS, VEHICLES
from core.legal_content import LEGAL_LINKS, LEGAL_PAGES, SUPPORT_LINKS
from core.reviews_content import TESTIMONIALS, TESTIMONIALS_SECTION_DESCRIPTION
from core.seo_content import (
    FAQ_ITEMS_SEO, FLEET_SLIDES_SEO, FOOTER_SEO, HERO_SEO, PRICING_PLANS_SEO, PRICING_SEO, RIDE_CARDS_SEO, RIDES_SEO,
    SAFETY_FEATURES_SEO, SAFETY_SEO, SITE_SEO, STAT_LINKS, STATS_SEO, STEPS_SECTION_SEO, STEPS_SEO, TESTIMONIALS_SECTION_SEO,
)

from core.models import (
    AboutSection, AboutValue, FAQItem, FAQSection, FooterColumn, LegalPage, FooterLink, FooterSettings, SocialLink,
    BookingModal, RentalPackage, TripRate, FleetSection, FleetSlide, FleetSpec, HeroSection, NavItem, PricingPlan, PricingSection, RideOption, RidesSection, SafetyFeature, SafetySection, SiteSettings, StatItem, Step, StepsSection, Testimonial, TestimonialsSection, VehicleClass,
)

SITE = {
    "site_name": "New Track",
    "logo_alt": "New Track",
    "nav_cta_text": "Book a Ride",
    "nav_cta_opens_booking": True,
    "nav_cta_link": "#book",
    "meta_title": "New Track | Your Destination – Our Vision",
    "meta_description": (
        "Fast, safe, and sustainable EV rides with NTTS Mobility. Real-time chauffeur tracking, "
        "premium EV fleets, upfront fares and zero surge pricing."
    ),
    "meta_keywords": "NTTS Mobility, EV cab, electric taxi, book a ride, airport transfer, chauffeur, urban mobility",
    "og_title": "New Track | Your Destination – Our Vision",
    "og_description": "Fast, safe, and sustainable EV rides with zero surge surprises.",
    "robots": "index, follow",
    **SITE_SEO,  # client SEO wording (core/seo_content.py)
}

NAV_ITEMS = [
    ("Home", "#home"),
    ("Fleet & Rides", "#fleet"),
    ("How It Works", "#how-it-works"),
    ("Safety", "#safety"),
    ("About Us", "#about"),
    ("Pricing", "#pricing"),
]

HERO = {
    "badge_text": "NEXT-GEN URBAN TRANSIT",
    "title": "Your Destination —",
    "title_highlight": "Our Vision",
    "description": (
        "Fast, safe, and sustainable rides at your fingertips. Experience the future of urban "
        "mobility with real-time network tracking, verified chauffeurs, premium EV fleets, and "
        "zero surge surprises."
    ),
    "background_alt": "Electric car driving on a forest road",
    "tracking_label": "Tracking Chauffeur",
    "vehicle_name": "NTTS Luxe EV",
    "vehicle_details": "Ioniq 5 / Tesla • Emerald",
    "fleet_label": "NTTS Fleet",
    "distance_text": "0.8 km away",
    "driver_name": "Rajesh S.",
    "driver_initials": "RS",
    "driver_rating": "4.98",
    "driver_trips": "(1,420 trips)",
    "card_title": "Book Instantly",
    "eta_text": "Avg ETA 30 mins",
    "pickup_label": "Pickup City",
    "pickup_placeholder": "Cyber City Hub, Gate 4",
    "destination_label": "Destination",
    "destination_placeholder": "International Tech Terminal 2",
    "date_label": "Date",
    "date_options": "Today (Instant)",
    "ride_window_label": "Ride Window",
    "ride_window_options": "Depart Now",
    "button_text": "Book a Ride",
    **HERO_SEO,  # client SEO wording (core/seo_content.py)
}

BOOKING = {
    "badge_text": "NTTS SHIELD™ PROTECTED",
    "subtitle": "Instant dispatch & guaranteed upfront fares across the city",
    **BOOKING_TEXT,  # trip tabs wording (core/booking_content.py)
    "local_terms": LOCAL_TERMS,
    "location_suggestions": "\n".join(CHENNAI_LOCATIONS),
    "contact_heading": "Your Details",
    "name_label": "Full Name",
    "name_placeholder": "Enter your name",
    "phone_label": "Mobile Number",
    "phone_placeholder": "Enter your mobile number",
    "email_label": "Email Address",
    "email_placeholder": "Enter your email",
    "button_prefix": "Book",
    "footer_note": "Free cancellation within 3 minutes of booking. Guaranteed zero surge pricing.",
    "success_title": "Request Sent!",
    "success_message": "Our new team member will contact you shortly.",
    "success_button_text": "Done",
    "success_footer_note": "Invitation expires in 7 days",
}

FLEET = {
    "eyebrow": "NTTS LIVE MOBILITY DECK",
    "title": "Dynamic Fleet in Motion",
    "footer_text": "Auto-synced telematics • Zero idle latency",
    "autoplay": True,
    "autoplay_seconds": 6,
}

# Exec SUV wording is from the design. Luxe Sedan and Smart City were not shown in the
# design, so their text is written in the same style (edit it in admin any time).
# "ride_card" = the Fleet & Rides card whose photo the slide uses.
FLEET_SLIDES = [
    {"tab_label": "Luxe Sedan", "tab_icon": "sedan", "badge_text": "ZERO-EMISSION LUXURY",
     "title": "NTTS Luxe Electric Sedan",
     "description": (
         "Whisper-quiet electric cabin with ambient lighting, ergonomic leather seating, "
         "onboard Wi-Fi, and a smooth zero-emission ride across the city."
     ),
     "image_alt": "NTTS Luxe Electric Sedan", "ride_card": "Electric EV Plus",
     "order": 1, "is_active": True,
     "specs": [("Cabin Space", "4 Seats"), ("Luggage", "2 Suitcases"),
               ("Drive", "100% Electric"), ("Rating", "★ 4.98")]},
    {"tab_label": "Smart City", "tab_icon": "city", "badge_text": "EVERYDAY CITY RIDES",
     "title": "NTTS Smart City Sedan",
     "description": (
         "Affordable air-conditioned sedans for quick city hops, office commutes, and daily "
         "errands, with verified drivers and upfront fares."
     ),
     "image_alt": "NTTS Smart City Sedan", "ride_card": "Compact Sedan",
     "order": 2, "is_active": True,
     "specs": [("Cabin Space", "4 Seats"), ("Luggage", "2 Bags"),
               ("Comfort", "Full AC"), ("Rating", "★ 4.90")]},
    {"tab_label": "Exec SUV", "tab_icon": "suv", "badge_text": "FIRST-CLASS CHAUFFEUR",
     "title": "NTTS Executive Grand SUV",
     "description": (
         "Expansive 6-passenger cabin with active noise cancellation, private Wi-Fi mesh, "
         "executive fold-out desks, and generous luggage hold."
     ),
     "image_alt": "NTTS Executive Grand SUV", "ride_card": "Spacious SUV",
     "order": 3, "is_active": True,
     "specs": [("Cabin Space", "6 Seats"), ("Luggage", "5 Suitcases"),
               ("Privacy Tint", "Grade A"), ("Rating", "★ 4.99")]},
]
for _slide in FLEET_SLIDES:
    _slide.update(FLEET_SLIDES_SEO[_slide["tab_label"]])  # client SEO wording (core/seo_content.py)

STATS = [
    {"number": "10M+", "show_star": False, "label": "Rides Completed Safely", "color": "green", "order": 1},
    {"number": "4.9", "show_star": True, "label": "Avg Customer Satisfaction", "color": "dark", "order": 2},
    {"number": "50+", "show_star": False, "label": "Metros & Cities Worldwide", "color": "navy", "order": 3},
    {"number": "24/7", "show_star": False, "label": "Human Concierge & Safety", "color": "green", "order": 4},
]
for _stat in STATS:
    _stat["label"] = STATS_SEO[_stat["number"]]  # client SEO wording (core/seo_content.py)
    _stat["link"] = STAT_LINKS.get(_stat["number"], "")

RIDES = {
    "badge_text": "FLEET & RIDES",
    "title": "Choose Your Ride",
    "description": "Tailored transportation solutions calibrated for speed, comfort, or solo sprints.",
    "side_badge_text": "100% Carbon-Neutral Fleet Options",
    **RIDES_SEO,  # client SEO wording (core/seo_content.py)
}
for _card in RIDE_OPTIONS:
    _card.update(RIDE_CARDS_SEO[_card["name"]])  # client SEO wording (core/seo_content.py)

STEPS_SECTION = {
    "badge_text": "THE PROCESS",
    "title": "Ride in 3 Simple Steps",
    "description": "From tapping your screen to stepping out at your destination—zero friction, all precision.",
    "step_word": "STEP",
    "show_banner": True,
    "banner_title": "Sub-Second Driver Allocation",
    "banner_text": "Our edge routing engine matches you with the ideal nearby partner in less than 400ms.",
    "banner_badge": "99.98% DISPATCH UPTIME",
    **STEPS_SECTION_SEO,  # client SEO wording (core/seo_content.py)
}

STEPS = [
    {"icon": "location", "color": "green", "title": "Enter Your Destination",
     "description": "Type in your pickup point or allow the geo-sensor to lock onto your precise spot automatically.",
     "highlight_text": "Instant GPS coordinate detection", "order": 1},
    {"icon": "sliders", "color": "blue", "title": "Choose Your Ride",
     "description": "Compare transparent upfront fares, precise vehicle models, and driver distance before locking in.",
     "highlight_text": "Locked fixed price — no surprises", "order": 2},
    {"icon": "shield", "color": "green", "title": "Sit Back & Relax",
     "description": "Track your driver's real-time trajectory, share ride details with loved ones, and pay cashlessly.",
     "highlight_text": "Encrypted telemetry & live track", "order": 3},
]
for _step in STEPS:
    _step.update(STEPS_SEO[_step["order"]])  # client SEO wording (core/seo_content.py)

SAFETY = {
    "badge_text": "",
    "title": "Your Safety is Our Priority",
    "description": (
        "From algorithmic background vetting to emergency rapid-response teams on standby, "
        "our security infrastructure protects every single kilometer."
    ),
    "show_highlight": True,
    "highlight_title": "NTTS Shield™ Active",
    "highlight_text": "Every trip automatically benefits from round-the-clock incident monitoring and insurance cover.",
    **SAFETY_SEO,  # client SEO wording (core/seo_content.py)
}

SAFETY_FEATURES = [
    {"icon": "id_card", "color": "green", "title": "Verified Drivers",
     "description": "Multi-point background and driving record screening before first dispatch.", "order": 1},
    {"icon": "satellite", "color": "blue", "title": "Live GPS Tracking",
     "description": "Share live telemetry links with contacts so they see your precise spot in real-time.", "order": 2},
    {"icon": "sos", "color": "red", "title": "SOS Emergency Button",
     "description": "Direct 1-tap pipeline to law enforcement and 24/7 internal emergency dispatch.", "order": 3},
    {"icon": "phone_lock", "color": "green", "title": "Masked Numbers",
     "description": "In-app VoIP and masked virtual phone routing keep your private number private.", "order": 4},
    {"icon": "handshake", "color": "green", "title": "2-Way Accountability",
     "description": "Mutual rating ensures both riders and drivers uphold highest decorum standards.", "order": 5},
    {"icon": "shield", "color": "blue", "title": "Accident Cover",
     "description": "Included comprehensive accidental and medical insurance for every booked ride.", "order": 6},
]
for _feature in SAFETY_FEATURES:
    _feature.update(SAFETY_FEATURES_SEO[_feature["order"]])  # client SEO wording (core/seo_content.py)

PRICING = {
    "badge_text": "TRANSPARENT TARIFF",
    "title": "Simple, Transparent Pricing",
    "description": "No hidden fuel fees. Upfront fares guaranteed before you confirm.",
    **PRICING_SEO,  # client SEO wording (core/seo_content.py)
}
for _plan in PRICING_PLANS:
    _plan.update(PRICING_PLANS_SEO[_plan["car"]])  # client SEO wording (core/seo_content.py)

TESTIMONIALS_SECTION = {
    "badge_text": "VERIFIED RIDERS",
    "title": "What Our Riders Say",
    "description": TESTIMONIALS_SECTION_DESCRIPTION,
    **TESTIMONIALS_SECTION_SEO,  # client SEO wording (core/seo_content.py)
}


FAQ_SECTION = {
    "is_active": True,
    "badge_text": "FAQ",
    "title": "Frequently Asked Questions",
    "description": "Everything you need to know about booking, fares and safety with New Track.",
    "show_help_box": True,
    "help_title": "Still have questions?",
    "help_text": "Our help desk team is happy to help you plan your ride.",
    "help_button_text": "Call Help Desk",
}

FAQ_ITEMS = [
    ("How do I book a ride?",
     "Tap “Book a Ride”, enter your pickup city and destination, choose a car and add your name, "
     "mobile number and email. Our team will call you shortly to confirm the booking."),
    ("How soon will my car arrive?",
     "For instant bookings, your car usually arrives within 30–40 minutes. "
     "If you need it at a fixed time, use the Schedule option while booking."),
    ("Can I book a ride in advance?",
     "Yes. Choose “Schedule” in the booking form and pick your pickup date and time."),
    ("How is the fare calculated?",
     "Each car type has a base fare plus a per-kilometre rate, shown in the Pricing section. "
     "The fare is shared with you upfront before you confirm."),
    ("Is there any surge pricing?",
     "No. We never apply surge pricing, so you pay the same fair rate at any time of the day."),
    ("Can I cancel my booking?",
     "Yes. Cancellation is free within 3 minutes of booking. "
     "After that, please call our help desk and we will assist you."),
    ("Are your drivers verified?",
     "Yes. Every driver goes through background and driving record checks before their first trip."),
    ("Do you offer airport transfers and outstation trips?",
     "Yes. Along with daily city rides, we offer airport pickups and drops and outstation trips. "
     "Book online or call our help desk to plan your trip."),
]
FAQ_ITEMS = FAQ_ITEMS_SEO  # client SEO wording (core/seo_content.py) replaces the questions above

FOOTER = {
    "about_text": (
        "Redefining mobility for the modern city. Experience seamless, safe, and sustainable "
        "transportation at the tap of a button."
    ),
    **FOOTER_SEO,  # client SEO wording (core/seo_content.py)
    "company_name": "Ntts Mobility Solutions Pvt Ltd",
    "address": "First Floor, Door No.4, East Spur Tank Road,\nEgmore, Chennai, Chennai, Tamil Nadu, 600008",
    "email": "info@newtrackindia.com",
    "helpdesk_label": "Help Desk",
    "helpdesk_phone": "9543024365",
    "landline_label": "Land Line",
    "landline_phone": "044-42146995",
    "copyright_text": "© {year} NTTS CAR RENTALS. All rights reserved.",
    "credit_text": "Designed & Developed by Vetri IT Systems",
    "credit_link": "https://vetriitsystems.com/",
    "whatsapp_number": "9543024365",
    "whatsapp_message": "Hi NTTS Mobility, I would like to book a ride.",
}

SOCIAL_LINKS = [("website", "#"), ("share", "#"), ("heart", "#")]

FOOTER_COLUMNS = [
    # Company = the same sections as the navbar menu
    ("COMPANY", [(label, link) for label, link in NAV_ITEMS]),
    # Support and Legal only link to things on this page (Legal links open the policy popups)
    ("SUPPORT", SUPPORT_LINKS),
    ("LEGAL", LEGAL_LINKS),
]


class Command(BaseCommand):
    help = "Seed website content (images are uploaded in admin)."

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Overwrite existing text with the design wording.")

    def singleton(self, model, values, reset):
        obj = model.load()
        if obj is None:
            obj = model(**values)
            obj.save()
            self.stdout.write(self.style.SUCCESS(f"  created {model._meta.verbose_name}"))
        elif reset:
            for key, value in values.items():
                setattr(obj, key, value)
            obj.save()
            self.stdout.write(self.style.WARNING(f"  reset {model._meta.verbose_name}"))
        else:
            filled = [key for key, value in values.items()
                      if getattr(obj, key) in ("", None) and value not in ("", None)]
            for key in filled:
                setattr(obj, key, values[key])
            if filled:
                obj.save()
                self.stdout.write(self.style.SUCCESS(f"  filled new fields in {model._meta.verbose_name}: {', '.join(filled)}"))
            else:
                self.stdout.write(f"  kept existing {model._meta.verbose_name}")
        return obj

    @transaction.atomic
    def handle(self, *args, reset=False, **options):
        self.stdout.write("Seeding content...")
        site = self.singleton(SiteSettings, SITE, reset)
        self.singleton(HeroSection, HERO, reset)
        about = self.singleton(AboutSection, ABOUT, reset)
        if reset or not about.values.exists():
            about.values.all().delete()
            for data in ABOUT_VALUES:
                AboutValue.objects.create(section=about, **data)
            self.stdout.write(self.style.SUCCESS(f"  {len(ABOUT_VALUES)} About Us value cards"))
        self.singleton(BookingModal, BOOKING, reset)

        if reset or not site.nav_items.exists():
            site.nav_items.all().delete()
            for i, (label, link) in enumerate(NAV_ITEMS, start=1):
                NavItem.objects.create(site=site, label=label, link=link, order=i)
            self.stdout.write(self.style.SUCCESS(f"  {len(NAV_ITEMS)} navbar links"))

        for data in VEHICLES:
            data = {k: v for k, v in data.items() if k != "old_names"}
            data["seats"] = SEATS.get(data["name"], 4)
            existing = VehicleClass.objects.filter(name=data["name"]).first()
            if existing is None:
                VehicleClass.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"  created vehicle {data['name']}"))
            elif reset:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.save()

        packages = {}
        for order, name in enumerate(RENTAL_PACKAGES, start=1):
            packages[name], _ = RentalPackage.objects.get_or_create(name=name, defaults={"order": order})
        added = 0
        for car in VehicleClass.objects.all():
            for row in rate_rows(car.name):
                package = packages.get(row.pop("package"))
                rate, created = TripRate.objects.get_or_create(
                    vehicle=car, trip_type=row.pop("trip_type"), package=package, defaults=row)
                if created:
                    added += 1
                elif reset:
                    TripRate.objects.filter(pk=rate.pk).update(**row)
        if added:
            self.stdout.write(self.style.SUCCESS(f"  {added} booking popup prices"))

        self.singleton(FleetSection, FLEET, reset)
        if reset or not StatItem.objects.exists():
            StatItem.objects.all().delete()
            for data in STATS:
                StatItem.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"  {len(STATS)} stat boxes"))

        self.singleton(RidesSection, RIDES, reset)
        for data in RIDE_OPTIONS:
            data = {k: v for k, v in data.items() if k != "old_names"}
            data = dict(data, currency_symbol="₹", price_suffix="base", image_alt=data["name"])
            data["booking_car"] = VehicleClass.objects.filter(name=data["booking_car"]).first()
            existing = RideOption.objects.filter(name=data["name"]).first()
            if existing is None:
                RideOption.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"  created ride card {data['name']}"))
            elif reset:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.save()

        for data in FLEET_SLIDES:
            data = dict(data)
            specs = data.pop("specs")
            data["ride_card"] = RideOption.objects.filter(name=data["ride_card"]).first()
            slide = FleetSlide.objects.filter(tab_label=data["tab_label"]).first()
            if slide is None:
                slide = FleetSlide.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"  created fleet slide {data['tab_label']}"))
            elif reset or not slide.description:
                # reset, or a slide that was only a placeholder (no text yet)
                for key, value in data.items():
                    setattr(slide, key, value)
                slide.save()
                slide.specs.all().delete()
                self.stdout.write(self.style.SUCCESS(f"  filled fleet slide {data['tab_label']}"))
            else:
                if slide.ride_card is None and data["ride_card"]:
                    slide.ride_card = data["ride_card"]
                    slide.save(update_fields=["ride_card"])
                    self.stdout.write(self.style.SUCCESS(f"  linked photo for fleet slide {data['tab_label']}"))
                continue
            for i, (label, value) in enumerate(specs, start=1):
                FleetSpec.objects.create(slide=slide, label=label, value=value, order=i)

        self.singleton(StepsSection, STEPS_SECTION, reset)
        if reset or not Step.objects.exists():
            Step.objects.all().delete()
            for data in STEPS:
                Step.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"  {len(STEPS)} steps"))

        self.singleton(SafetySection, SAFETY, reset)
        if reset or not SafetyFeature.objects.exists():
            SafetyFeature.objects.all().delete()
            for data in SAFETY_FEATURES:
                SafetyFeature.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"  {len(SAFETY_FEATURES)} safety feature cards"))

        self.singleton(PricingSection, PRICING, reset)
        for data in PRICING_PLANS:
            data = {k: v for k, v in data.items() if k != "old_titles"}
            data = dict(data, price_suffix="/ base fare")
            data["car"] = VehicleClass.objects.filter(name=data["car"]).first()
            if data["car"] is None:
                self.stdout.write(self.style.ERROR(f"  skipped plan {data['title']}: its car is missing"))
                continue
            existing = PricingPlan.objects.filter(title=data["title"]).first()
            if existing is None:
                PricingPlan.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"  created pricing plan {data['title']}"))
            elif reset:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.save()

        self.singleton(TestimonialsSection, TESTIMONIALS_SECTION, reset)
        if reset or not Testimonial.objects.exists():
            Testimonial.objects.all().delete()
            for data in TESTIMONIALS:
                Testimonial.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"  {len(TESTIMONIALS)} testimonials"))

        self.singleton(FAQSection, FAQ_SECTION, reset)
        if reset or not FAQItem.objects.exists():
            FAQItem.objects.all().delete()
            for i, (question, answer) in enumerate(FAQ_ITEMS, start=1):
                FAQItem.objects.create(question=question, answer=answer, order=i)
            self.stdout.write(self.style.SUCCESS(f"  {len(FAQ_ITEMS)} FAQ questions"))

        footer = self.singleton(FooterSettings, FOOTER, reset)
        if reset or not footer.social_links.exists():
            footer.social_links.all().delete()
            for i, (platform, link) in enumerate(SOCIAL_LINKS, start=1):
                SocialLink.objects.create(footer=footer, platform=platform, link=link, order=i)
            self.stdout.write(self.style.SUCCESS(f"  {len(SOCIAL_LINKS)} social icons"))
        if reset or not FooterColumn.objects.exists():
            FooterColumn.objects.all().delete()
            for i, (title, labels) in enumerate(FOOTER_COLUMNS, start=1):
                column = FooterColumn.objects.create(title=title, order=i)
                for j, item in enumerate(labels, start=1):
                    label, link = item if isinstance(item, tuple) else (item, "#")
                    FooterLink.objects.create(column=column, label=label, link=link, order=j)
            self.stdout.write(self.style.SUCCESS(f"  {len(FOOTER_COLUMNS)} footer link columns"))

        for data in LEGAL_PAGES:
            existing = LegalPage.objects.filter(slug=data["slug"]).first()
            if existing is None:
                LegalPage.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"  created policy popup {data['title']}"))
            elif reset:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.save()

        self.stdout.write(self.style.SUCCESS("Done. Upload images in admin: logo, hero background, car options, fleet slides, ride cards, testimonial photos."))
