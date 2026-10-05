import logging
import threading
from datetime import timedelta

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import MAX_DAYS_AHEAD, MAX_PAX, MAX_TRIP_DAYS, MIN_LEAD_MINUTES, BookingForm
from .models import AboutSection, BookingModal, FAQItem, FAQSection, Testimonial, TestimonialsSection, PricingPlan, PricingSection, BookingRequest, FleetSection, FleetSlide, HeroSection, LegalPage, RentalPackage, RideOption, RidesSection, SafetyFeature, SafetySection, StatItem, Step, StepsSection, TRIP_TYPES, TripRate, VehicleClass
from .utils import send_booking_emails

logger = logging.getLogger(__name__)


def home(request):
    vehicles = list(VehicleClass.objects.filter(is_active=True).prefetch_related("ride_cards"))
    # No car is pre-selected unless one is marked "Picked by default" in admin
    default_vehicle = next((v for v in vehicles if v.is_default), None)
    booking = BookingModal.load()
    rates = list(TripRate.objects.filter(is_active=True, vehicle__is_active=True)
                 .exclude(package__is_active=False).select_related("vehicle", "package").prefetch_related("vehicle__ride_cards"))
    # Packages that at least one car has a price for
    packages = [p for p in RentalPackage.objects.filter(is_active=True) if any(r.package_id == p.pk for r in rates)]
    tab_labels = {
        "airport": booking.airport_tab_label, "local": booking.local_tab_label,
        "outstation": booking.outstation_tab_label,
    } if booking else {}
    trip_tabs = [{"value": value, "label": tab_labels.get(value, label),
                  "rates": [r for r in rates if r.trip_type == value]} for value, label in TRIP_TYPES]
    return render(request, "core/index.html", {
        "hero": HeroSection.load(),
        "about": AboutSection.objects.filter(is_active=True).prefetch_related("values").first(),
        "booking": booking,
        "vehicles": vehicles,
        "default_vehicle": default_vehicle,
        "trip_tabs": trip_tabs,
        "rental_packages": packages,
        "today": timezone.localdate(),
        "last_booking_date": timezone.localdate() + timedelta(days=MAX_DAYS_AHEAD),
        "booking_limits": {"min_lead_minutes": MIN_LEAD_MINUTES, "max_days_ahead": MAX_DAYS_AHEAD,
                           "max_trip_days": MAX_TRIP_DAYS, "max_pax": MAX_PAX},
        "fleet": FleetSection.load(),
        "fleet_slides": FleetSlide.objects.filter(is_active=True).select_related("ride_card").prefetch_related("specs"),
        "stats": StatItem.objects.filter(is_active=True),
        "rides": RidesSection.load(),
        "ride_options": RideOption.objects.filter(is_active=True).select_related("booking_car"),
        "steps_section": StepsSection.load(),
        "steps": Step.objects.filter(is_active=True),
        "safety": SafetySection.load(),
        "safety_features": SafetyFeature.objects.filter(is_active=True),
        "pricing": PricingSection.load(),
        "pricing_plans": PricingPlan.objects.filter(is_active=True).select_related("car"),
        "testimonials_section": TestimonialsSection.load(),
        "testimonials": Testimonial.objects.filter(is_active=True),
        "faq": FAQSection.objects.filter(is_active=True).first(),
        "faq_items": FAQItem.objects.filter(is_active=True),
        "legal_pages": LegalPage.objects.filter(is_active=True),
    })


def client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    return forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR")


def email_booking(booking_id):
    booking = BookingRequest.objects.get(pk=booking_id)
    try:
        send_booking_emails(booking)
        BookingRequest.objects.filter(pk=booking_id).update(email_sent=True)
    except Exception:
        logger.exception("Booking #%s saved but email could not be sent", booking_id)
    finally:
        connection.close()


@require_POST
def book_ride(request):
    form = BookingForm(request.POST)
    if not form.is_valid():
        errors = {field: errs[0] for field, errs in form.errors.items()}
        return JsonResponse({"ok": False, "errors": errors}, status=400)

    data = form.cleaned_data
    rate = data["rate"]
    vehicle = rate.vehicle
    booking = BookingRequest.objects.create(
        trip_type=data["trip_type"],
        pickup=data["pickup"],
        destination=data["destination"],
        ride_type=BookingRequest.SCHEDULE,
        scheduled_date=data["scheduled_date"],
        scheduled_time=data["scheduled_time"],
        date_option=data["date_option"],
        ride_window=data["ride_window"],
        flight_number=data["flight_number"],
        package_name=rate.package.name if rate.package_id else "",
        num_days=data["num_days"],
        num_pax=data["num_pax"],
        vehicle=vehicle,
        vehicle_name=vehicle.name,
        quoted_price=rate.quote,
        extra_charges=rate.extras,
        name=data["name"],
        phone=data["phone"],
        email=data["email"],
        ip_address=client_ip(request),
    )

    # Email is sent in the background so the customer sees the success popup instantly.
    # The booking is already saved, so nothing is lost if the email fails.
    threading.Thread(target=email_booking, args=(booking.pk,), daemon=True).start()

    return JsonResponse({"ok": True})
