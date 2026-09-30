"""
Seed the landing page content with the wording from the design.

    python manage.py seed_content           # only fills what is missing
    python manage.py seed_content --reset   # overwrite text back to the design wording

Images are never touched; upload them in the admin panel.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    AppDownloadSection, FooterColumn, FooterLink, FooterSettings, SocialLink,
    BookingModal, FleetSection, FleetSlide, FleetSpec, HeroSection, NavItem, PricingPlan, PricingSection, RideOption, RidesSection, SafetyFeature, SafetySection, SiteSettings, StatItem, Step, StepsSection, Testimonial, TestimonialsSection, VehicleClass,
)

SITE = {
    "site_name": "NTTS Mobility",
    "logo_alt": "NTTS Mobility",
    "nav_cta_text": "Book a Ride",
    "nav_cta_opens_booking": True,
    "nav_cta_link": "#book",
    "meta_title": "NTTS Mobility | Your Ride, Your Way – Anytime, Anywhere",
    "meta_description": (
        "Fast, safe, and sustainable EV rides with NTTS Mobility. Real-time chauffeur tracking, "
        "premium EV fleets, upfront fares and zero surge pricing."
    ),
    "meta_keywords": "NTTS Mobility, EV cab, electric taxi, book a ride, airport transfer, chauffeur, urban mobility",
    "og_title": "NTTS Mobility | Your Ride, Your Way",
    "og_description": "Fast, safe, and sustainable EV rides with zero surge surprises.",
    "robots": "index, follow",
}

NAV_ITEMS = [
    ("Home", "#home"),
    ("Fleet & Rides", "#fleet"),
    ("How It Works", "#how-it-works"),
    ("Safety", "#safety"),
    ("Pricing", "#pricing"),
]

HERO = {
    "badge_text": "NEXT-GEN URBAN TRANSIT",
    "title": "Your Ride, Your Way —",
    "title_highlight": "Anytime, Anywhere",
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
    "eta_text": "Avg ETA 2.4 min",
    "pickup_label": "Pickup Point",
    "pickup_placeholder": "Cyber City Hub, Gate 4",
    "destination_label": "Destination",
    "destination_placeholder": "International Tech Terminal 2",
    "date_label": "Date",
    "date_options": "Today (Instant)",
    "ride_window_label": "Ride Window",
    "ride_window_options": "Depart Now",
    "button_text": "Book a Ride",
}

BOOKING = {
    "badge_text": "NTTS SHIELD™ PROTECTED",
    "title": "Book Your Ride",
    "subtitle": "Instant dispatch & guaranteed upfront fares across the city",
    "pickup_label": "Pickup Point",
    "pickup_placeholder": "Cyber City Hub, Gate 4",
    "destination_label": "Destination",
    "destination_placeholder": "Airport terminal",
    "ride_now_label": "Ride Now",
    "schedule_label": "Schedule",
    "departing_label": "Departing:",
    "departing_highlight": "Within 3–5 Mins",
    "departing_note": "(Fastest match)",
    "schedule_date_label": "Pickup Date",
    "schedule_time_label": "Pickup Time",
    "vehicle_heading": "Select Vehicle Class",
    "nearby_suffix": "options nearby",
    "contact_heading": "Your Details",
    "name_label": "Full Name",
    "name_placeholder": "Enter your name",
    "phone_label": "Mobile Number",
    "phone_placeholder": "Enter your mobile number",
    "email_label": "Email Address",
    "email_placeholder": "Enter your email",
    "button_prefix": "Request",
    "footer_note": "Free cancellation within 3 minutes of booking. Guaranteed zero surge pricing.",
    "success_title": "Request Sent!",
    "success_message": "Our new team member will contact you shortly.",
    "success_button_text": "Done",
    "success_footer_note": "Invitation expires in 7 days",
}

VEHICLES = [
    {"name": "Compact Sedan", "button_name": "Compact Sedan", "details": "4 seats · 3m away",
     "base_price": Decimal("80"), "badge_text": "", "is_default": False, "order": 1},
    {"name": "Executive Sedan", "button_name": "Executive Sedan", "details": "Luxury AC · 5m away",
     "base_price": Decimal("140"), "badge_text": "", "is_default": False, "order": 2},
    {"name": "NTTS Luxe EV", "button_name": "NTTS Luxe", "details": "EV Whisper · 2m away",
     "base_price": Decimal("200"), "badge_text": "POPULAR", "is_default": True, "order": 3},
    {"name": "Spacious SUV", "button_name": "Spacious SUV", "details": "6–7 seats · 6m away",
     "base_price": Decimal("260"), "badge_text": "", "is_default": False, "order": 4},
]

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

STATS = [
    {"number": "10M+", "show_star": False, "label": "Rides Completed Safely", "color": "green", "order": 1},
    {"number": "4.9", "show_star": True, "label": "Avg Customer Satisfaction", "color": "dark", "order": 2},
    {"number": "50+", "show_star": False, "label": "Metros & Cities Worldwide", "color": "navy", "order": 3},
    {"number": "24/7", "show_star": False, "label": "Human Concierge & Safety", "color": "green", "order": 4},
]

RIDES = {
    "badge_text": "FLEET & RIDES",
    "title": "Choose Your Ride",
    "description": "Tailored transportation solutions calibrated for speed, comfort, or solo sprints.",
    "side_badge_text": "100% Carbon-Neutral Fleet Options",
}

# "booking_car" = the car picked in the booking popup when the card's button is clicked
RIDE_OPTIONS = [
    {"name": "Compact Sedan", "base_price": Decimal("80"), "badge_text": "",
     "description": "Affordable daily commutes with reliable drivers and quiet air-conditioned sedan cabins.",
     "features": "4 Seats\nAC Sedan\nLuggage 2x", "button_text": "Book Sedan",
     "booking_car": "Compact Sedan", "is_featured": False, "order": 1},
    {"name": "Premium Executive", "base_price": Decimal("200"), "badge_text": "TOP TIER",
     "description": "Luxury executive travel with top-tier amenities, EV sedans, and master-level chauffeurs.",
     "features": "EV / Audi / Tesla\nWi-Fi & Mags\nPriority Pickup", "button_text": "Book Premium",
     "booking_car": "Executive Sedan", "is_featured": True, "order": 2},
    {"name": "Spacious SUV", "base_price": Decimal("150"), "badge_text": "FAMILY & GROUP",
     "description": "Expansive 6-seater cabin engineered for group trips, family airport travel, and generous luggage.",
     "features": "6 Seats\nMassive Boot\nDual-Zone AC", "button_text": "Book SUV",
     "booking_car": "Spacious SUV", "is_featured": False, "order": 3},
    {"name": "Electric EV Plus", "base_price": Decimal("110"), "badge_text": "ECO SMART",
     "description": "100% green zero-emission electric sedans and crossovers with whisper-quiet ride telemetry.",
     "features": "4 Passengers\nZero Emission\nSilent Cabin", "button_text": "Book EV Plus",
     "booking_car": "NTTS Luxe EV", "is_featured": False, "order": 4},
]

STEPS_SECTION = {
    "badge_text": "THE PROCESS",
    "title": "Ride in 3 Simple Steps",
    "description": "From tapping your screen to stepping out at your destination—zero friction, all precision.",
    "step_word": "STEP",
    "show_banner": True,
    "banner_title": "Sub-Second Driver Allocation",
    "banner_text": "Our edge routing engine matches you with the ideal nearby partner in less than 400ms.",
    "banner_badge": "99.98% DISPATCH UPTIME",
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

SAFETY = {
    "badge_text": "ISO 27001 CERTIFIED SAFETY",
    "title": "Your Safety is Our Priority",
    "description": (
        "From algorithmic background vetting to emergency rapid-response teams on standby, "
        "our security infrastructure protects every single kilometer."
    ),
    "show_highlight": True,
    "highlight_title": "NTTS Shield™ Active",
    "highlight_text": "Every trip automatically benefits from round-the-clock incident monitoring and insurance cover.",
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

PRICING = {
    "badge_text": "TRANSPARENT TARIFF",
    "title": "Simple, Transparent Pricing",
    "description": "No hidden fuel fees. Upfront fares guaranteed before you confirm.",
}

# "car" = name of the car in the booking popup; the price comes from that car
PRICING_PLANS = [
    {"title": "COMPACT SEDAN", "color": "dark", "icon": "sedan", "car": "Compact Sedan", "badge_text": "", "is_featured": False,
     "features": "₹14 per additional KM\n4 Passengers Max\nFull Air-Conditioned\nBoot Space for 2 Bags",
     "button_text": "Select Sedan", "order": 1},
    {"title": "EXECUTIVE SEDAN", "color": "navy", "icon": "executive", "car": "Executive Sedan", "badge_text": "", "is_featured": False,
     "features": "₹18 per additional KM\n4 Executive Leather Seats\nBottled Water & Wi-Fi\nTop Chauffeur (4.9★)",
     "button_text": "Select Executive", "order": 2},
    {"title": "NTTS LUXE EV", "color": "green", "icon": "ev", "car": "NTTS Luxe EV", "badge_text": "MOST POPULAR", "is_featured": True,
     "features": "₹24 per additional KM\n4 Luxury Ergonomic Seats\nZero-Emission Electric Whisper Drive\n"
                 "Priority Pickup & Concierge",
     "button_text": "Select Luxe", "order": 3},
    {"title": "SPACIOUS SUV / XL", "color": "navy", "icon": "suv", "car": "Spacious SUV", "badge_text": "", "is_featured": False,
     "features": "₹28 per additional KM\n6–7 Passengers Max\nMassive Boot for 5+ Bags\nDual-Zone Climate Control",
     "button_text": "Select SUV", "order": 4},
]

TESTIMONIALS_SECTION = {
    "badge_text": "VERIFIED RIDERS",
    "title": "What Our Riders Say",
    "description": (
        "Thousands of daily commuters rely on NTTS Mobility for punctual meetings, "
        "late-night flights, and stress-free city hops."
    ),
}

TESTIMONIALS = [
    {"rating": 5, "name": "Priya Sharma", "role": "Daily Tech Commuter", "detail": "340+ rides", "order": 1,
     "quote": "The punctuality and EV silence make all the difference. NTTS Mobility is now the official "
              "transit app for our entire engineering group."},
    {"rating": 5, "name": "Marcus Vance", "role": "Managing Director", "detail": "Executive Rider", "order": 2,
     "quote": "For investor meetings and airport transfers, NTTS Luxe is unmatched. Impeccable electric sedans, "
              "silence during phone conferences, and never a cancellation."},
    {"rating": 5, "name": "Dr. Ananya Roy", "role": "Night Physician", "detail": "190+ trips", "order": 3,
     "quote": "As an on-call physician, I need zero delays at 2 AM. The driver background checks and "
              "emergency SOS give immense peace of mind."},
]

APP_DOWNLOAD = {
    "is_active": True,
    "badge_text": "AVAILABLE ON IOS & ANDROID",
    "title": "Ready to Move?",
    "title_highlight": "Download NTTS Mobility Today",
    "text_before_code": "Get ₹150 off your first 3 rides with promo code",
    "promo_code": "NTTSGO",
    "text_after_code": ". Instant onboarding in 60 seconds.",
    "show_app_store": True,
    "app_store_small_text": "DOWNLOAD ON THE",
    "app_store_text": "Apple App Store",
    "show_google_play": True,
    "google_play_small_text": "GET IT ON",
    "google_play_text": "Google Play",
    "show_qr": True,
    "qr_title": "Scan to Download",
    "qr_subtitle": "Instant Camera Link",
}

FOOTER = {
    "about_text": (
        "Redefining mobility for the modern city. Experience seamless, safe, and sustainable "
        "transportation at the tap of a button."
    ),
    "company_name": "Ntts Mobility Solutions Pvt Ltd",
    "address": "First Floor, Door No.4, East Spur Tank Road,\nEgmore, Chennai, Chennai, Tamil Nadu, 600008",
    "email": "info@newtrackindia.com",
    "helpdesk_label": "Help Desk",
    "helpdesk_phone": "9543024365",
    "landline_label": "Land Line",
    "landline_phone": "044-42146995",
    "copyright_text": "© 2024 NTTS Mobility Technologies. All rights reserved.",
    "credit_text": "Designed & Developed by Vetri IT Systems",
    "credit_link": "https://vetriitsystems.com/",
    "whatsapp_number": "9543024365",
    "whatsapp_message": "Hi NTTS Mobility, I would like to book a ride.",
}

SOCIAL_LINKS = [("website", "#"), ("share", "#"), ("heart", "#")]

FOOTER_COLUMNS = [
    ("COMPANY", ["About Us", "Careers", "Press", "Blog"]),
    ("SUPPORT", ["Help Center", "Safety Protocols", "Policy", "Contact Concierge"]),
    ("LEGAL", ["Privacy Policy", "Terms of Transit"]),
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
            filled = [key for key, value in values.items() if getattr(obj, key) in ("", None)]
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
        self.singleton(BookingModal, BOOKING, reset)

        if reset or not site.nav_items.exists():
            site.nav_items.all().delete()
            for i, (label, link) in enumerate(NAV_ITEMS, start=1):
                NavItem.objects.create(site=site, label=label, link=link, order=i)
            self.stdout.write(self.style.SUCCESS(f"  {len(NAV_ITEMS)} navbar links"))

        for data in VEHICLES:
            existing = VehicleClass.objects.filter(name=data["name"]).first()
            if existing is None:
                VehicleClass.objects.create(**data)
                self.stdout.write(self.style.SUCCESS(f"  created vehicle {data['name']}"))
            elif reset:
                for key, value in data.items():
                    setattr(existing, key, value)
                existing.save()

        self.singleton(FleetSection, FLEET, reset)
        if reset or not StatItem.objects.exists():
            StatItem.objects.all().delete()
            for data in STATS:
                StatItem.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"  {len(STATS)} stat boxes"))

        self.singleton(RidesSection, RIDES, reset)
        for data in RIDE_OPTIONS:
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

        self.singleton(AppDownloadSection, APP_DOWNLOAD, reset)

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
                for j, label in enumerate(labels, start=1):
                    FooterLink.objects.create(column=column, label=label, link="#", order=j)
            self.stdout.write(self.style.SUCCESS(f"  {len(FOOTER_COLUMNS)} footer link columns"))

        self.stdout.write(self.style.SUCCESS("Done. Upload images in admin: logo, hero background, car options, fleet slides, ride cards, testimonial photos, app QR code."))
