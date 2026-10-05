import re
import unicodedata
from datetime import datetime, timedelta

from django import forms
from django.core.validators import validate_email
from django.utils import timezone

from .models import AIRPORT, LOCAL, OUTSTATION, TRIP_TYPES, TripRate

# Indian mobile: 10 digits starting with 6, 7, 8 or 9.
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
EMAIL_DOMAIN_RE = re.compile(r"^(?!-)[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$")
# Flight number: airline code (2 characters with a letter, or 3 letters) + 1–4 digits,
# e.g. 6E 2134, AI 202, UK811A, IGO 123
FLIGHT_RE = re.compile(r"^([A-Z]{3}|[A-Z][A-Z0-9]|[0-9][A-Z])(\d{1,4}[A-Z]?)$")
ADDRESS_EXTRA_CHARS = " ,.-/#()&':;+"

# Booking limits (keep in sync with static/js/main.js)
MIN_LEAD_MINUTES = 30      # pickup must be at least this far from now
MAX_DAYS_AHEAD = 90        # bookings open this many days ahead
MAX_TRIP_DAYS = 30         # outstation: no of days
MAX_PAX = 20               # outstation: no of passengers (also limited by the car's seats)


def is_valid_name(name):
    """Letters in any language (incl. Tamil/Hindi vowel signs), spaces, dot, apostrophe, hyphen.
    Must start with a letter."""
    if not unicodedata.category(name[0]).startswith("L"):
        return False
    return all(unicodedata.category(ch)[0] in "LM" or ch in " .'-" for ch in name)


def clean_address(value, label):
    """Letters (any language), numbers and the usual address signs: , . - / # ( ) & ' : ; +"""
    value = " ".join((value or "").split())
    if not value:
        raise forms.ValidationError(f"Please enter the {label}.")
    if not all(unicodedata.category(ch)[0] in "LMN" or ch in ADDRESS_EXTRA_CHARS for ch in value):
        raise forms.ValidationError("Only letters, numbers and , . - / # ( ) & ' are allowed.")
    if sum(unicodedata.category(ch).startswith("L") for ch in value) < 3:
        raise forms.ValidationError(f"Please enter a proper {label}.")
    if len(value) > 200:
        raise forms.ValidationError("Address is too long (max 200 characters).")
    return value


def clean_number(value, label, low, high):
    value = (value or "").strip()
    if not value:
        raise forms.ValidationError(f"Please enter the {label}.")
    if not value.isdigit():
        raise forms.ValidationError(f"{label[0].upper()}{label[1:]} must be a whole number.")
    number = int(value)
    if not low <= number <= high:
        raise forms.ValidationError(f"Please enter between {low} and {high}.")
    return number


def normalize_mobile(raw):
    """Accepts 98765 43210, +91 98765-43210, 09876543210 … and returns the 10 digits."""
    digits = re.sub(r"[\s\-().]", "", raw or "")
    if digits.startswith("+91"):
        digits = digits[3:]
    elif len(digits) == 12 and digits.startswith("91"):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith("0"):
        digits = digits[1:]
    return digits


class BookingForm(forms.Form):
    trip_type = forms.ChoiceField(
        choices=TRIP_TYPES,
        error_messages={"required": "Please choose a trip type.", "invalid_choice": "Please choose a trip type."},
    )
    pickup = forms.CharField(max_length=255, required=False)
    destination = forms.CharField(max_length=255, required=False)
    scheduled_date = forms.DateField(required=False, error_messages={"invalid": "Please choose a valid date."})
    scheduled_time = forms.TimeField(required=False, error_messages={"invalid": "Please choose a valid time."})
    date_option = forms.CharField(max_length=60, required=False)
    ride_window = forms.CharField(max_length=60, required=False)
    flight_number = forms.CharField(max_length=20, required=False)
    num_days = forms.CharField(max_length=5, required=False)
    num_pax = forms.CharField(max_length=5, required=False)
    rate = forms.ModelChoiceField(
        queryset=TripRate.objects.filter(is_active=True, vehicle__is_active=True)
        .exclude(package__is_active=False).select_related("vehicle", "package"),
        error_messages={"required": "Please choose a car.", "invalid_choice": "Please choose a car."},
    )
    name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=254, required=False)
    website = forms.CharField(required=False)  # honeypot, must stay empty

    def clean_pickup(self):
        return clean_address(self.cleaned_data["pickup"], "pickup address")

    def clean_name(self):
        name = " ".join(self.cleaned_data["name"].split())
        if not name:
            raise forms.ValidationError("Please enter your name.")
        if not is_valid_name(name):
            raise forms.ValidationError("Name can only contain letters and spaces.")
        letters = sum(unicodedata.category(ch).startswith("L") for ch in name)
        if letters < 2:
            raise forms.ValidationError("Please enter your full name.")
        if len(name) > 50:
            raise forms.ValidationError("Name is too long (max 50 characters).")
        return name

    def clean_phone(self):
        raw = self.cleaned_data["phone"].strip()
        if not raw:
            raise forms.ValidationError("Please enter your mobile number.")
        digits = normalize_mobile(raw)
        if not digits.isdigit() or len(digits) != 10:
            raise forms.ValidationError("Mobile number must be 10 digits.")
        if not MOBILE_RE.match(digits):
            raise forms.ValidationError("Enter a valid Indian mobile number (starts with 6, 7, 8 or 9).")
        if len(set(digits)) == 1:
            raise forms.ValidationError("Please enter a real mobile number.")
        return f"+91 {digits[:5]} {digits[5:]}"

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not email:
            raise forms.ValidationError("Please enter your email address.")
        try:
            validate_email(email)
        except forms.ValidationError:
            raise forms.ValidationError("Please enter a valid email address, e.g. name@gmail.com.")
        local, _, domain = email.rpartition("@")
        if ".." in email or local.startswith(".") or local.endswith(".") or not EMAIL_DOMAIN_RE.match(domain):
            raise forms.ValidationError("Please enter a valid email address, e.g. name@gmail.com.")
        return email

    def clean_flight_number(self):
        raw = self.cleaned_data["flight_number"]
        compact = re.sub(r"[\s-]", "", raw or "").upper()
        if not compact:
            return ""  # required only for Airport Transfer (checked in clean)
        match = FLIGHT_RE.match(compact)
        if not match:
            raise forms.ValidationError("Enter a valid flight number, e.g. 6E 2134.")
        return f"{match.group(1)} {match.group(2)}"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Spam detected.")
        trip = cleaned.get("trip_type")
        rate = cleaned.get("rate")

        # Car must belong to the chosen tab
        if trip and rate and rate.trip_type != trip:
            self.add_error("rate", "Please choose a car.")
            rate = cleaned["rate"] = None

        # Drop: only on the Airport tab, and not the same as the pickup
        if trip == AIRPORT:
            try:
                cleaned["destination"] = clean_address(cleaned.get("destination"), "drop address")
            except forms.ValidationError as error:
                self.add_error("destination", error)
            else:
                pickup = cleaned.get("pickup")
                if pickup and pickup.casefold() == cleaned["destination"].casefold():
                    self.add_error("destination", "Drop address can't be the same as the pickup.")
            if not cleaned.get("flight_number") and "flight_number" not in self.errors:
                self.add_error("flight_number", "Please enter the flight number.")
        else:
            cleaned["destination"] = cleaned["flight_number"] = ""

        # Pickup date & time: both needed, not in the past, at least 30 min from now, max 90 days ahead
        date, time = cleaned.get("scheduled_date"), cleaned.get("scheduled_time")
        today = timezone.localdate()
        if not date:
            if "scheduled_date" not in self.errors:
                self.add_error("scheduled_date", "Please choose a pickup date.")
        elif date < today:
            self.add_error("scheduled_date", "Pickup date can't be in the past.")
        elif date > today + timedelta(days=MAX_DAYS_AHEAD):
            self.add_error("scheduled_date", f"You can book up to {MAX_DAYS_AHEAD} days ahead.")
        if not time:
            if "scheduled_time" not in self.errors:
                self.add_error("scheduled_time", "Please choose a pickup time.")
        elif date and "scheduled_date" not in self.errors:
            pickup_at = timezone.make_aware(datetime.combine(date, time))
            if pickup_at < timezone.now() + timedelta(minutes=MIN_LEAD_MINUTES):
                self.add_error("scheduled_time", f"Pickup time must be at least {MIN_LEAD_MINUTES} minutes from now.")

        # Outstation: no of days and passengers (passengers can't be more than the car's seats)
        if trip == OUTSTATION:
            for field, label, high in (("num_days", "no of days", MAX_TRIP_DAYS), ("num_pax", "no of pax", MAX_PAX)):
                try:
                    cleaned[field] = clean_number(cleaned.get(field), label, 1, high)
                except forms.ValidationError as error:
                    cleaned[field] = None
                    self.add_error(field, error)
            pax = cleaned.get("num_pax")
            if rate and pax and pax > rate.vehicle.seats:
                self.add_error("rate", f"{rate.vehicle.name} seats up to {rate.vehicle.seats}. "
                                       f"Please choose a bigger car.")
        else:
            cleaned["num_days"] = cleaned["num_pax"] = None
        return cleaned
