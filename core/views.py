import logging
import threading

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import BookingForm
from .models import AppDownloadSection, BookingModal, Testimonial, TestimonialsSection, PricingPlan, PricingSection, BookingRequest, FleetSection, FleetSlide, HeroSection, RideOption, RidesSection, SafetyFeature, SafetySection, StatItem, Step, StepsSection, VehicleClass
from .utils import send_booking_emails

logger = logging.getLogger(__name__)


def home(request):
    vehicles = list(VehicleClass.objects.filter(is_active=True).prefetch_related("ride_cards"))
    default_vehicle = next((v for v in vehicles if v.is_default), vehicles[0] if vehicles else None)
    return render(request, "core/index.html", {
        "hero": HeroSection.load(),
        "booking": BookingModal.load(),
        "vehicles": vehicles,
        "default_vehicle": default_vehicle,
        "today": timezone.localdate(),
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
        "app_download": AppDownloadSection.objects.filter(is_active=True).first(),
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
    vehicle = data["vehicle"]
    booking = BookingRequest.objects.create(
        pickup=data["pickup"],
        destination=data["destination"],
        ride_type=data["ride_type"],
        scheduled_date=data["scheduled_date"],
        scheduled_time=data["scheduled_time"],
        date_option=data["date_option"],
        ride_window=data["ride_window"],
        vehicle=vehicle,
        vehicle_name=vehicle.name,
        quoted_price=f"{vehicle.price_display} {vehicle.price_suffix}".strip(),
        name=data["name"],
        phone=data["phone"],
        email=data["email"],
        ip_address=client_ip(request),
    )

    # Email is sent in the background so the customer sees the success popup instantly.
    # The booking is already saved, so nothing is lost if the email fails.
    threading.Thread(target=email_booking, args=(booking.pk,), daemon=True).start()

    return JsonResponse({"ok": True})
