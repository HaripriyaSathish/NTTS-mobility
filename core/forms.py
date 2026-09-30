import re
import unicodedata

from django import forms
from django.core.validators import validate_email
from django.utils import timezone

from .models import BookingRequest, VehicleClass

# Indian mobile: 10 digits starting with 6, 7, 8 or 9.
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")
EMAIL_DOMAIN_RE = re.compile(r"^(?!-)[a-z0-9-]+(\.[a-z0-9-]+)*\.[a-z]{2,}$")


def is_valid_name(name):
    """Letters in any language (incl. Tamil/Hindi vowel signs), spaces, dot, apostrophe, hyphen.
    Must start with a letter."""
    if not unicodedata.category(name[0]).startswith("L"):
        return False
    return all(unicodedata.category(ch)[0] in "LM" or ch in " .'-" for ch in name)


def clean_address(value, label):
    # Addresses can contain anything: letters, numbers, commas, #, /, - etc.
    # They only need to be filled in.
    value = " ".join((value or "").split())
    if not value:
        raise forms.ValidationError(f"Please enter your {label}.")
    return value


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
    pickup = forms.CharField(max_length=255, required=False)
    destination = forms.CharField(max_length=255, required=False)
    ride_type = forms.ChoiceField(choices=BookingRequest.RIDE_TYPES, required=False)
    scheduled_date = forms.DateField(required=False)
    scheduled_time = forms.TimeField(required=False)
    date_option = forms.CharField(max_length=60, required=False)
    ride_window = forms.CharField(max_length=60, required=False)
    vehicle = forms.ModelChoiceField(
        queryset=VehicleClass.objects.filter(is_active=True),
        error_messages={"required": "Please choose a car.", "invalid_choice": "Please choose a car."},
    )
    name = forms.CharField(max_length=100, required=False)
    phone = forms.CharField(max_length=20, required=False)
    email = forms.CharField(max_length=254, required=False)
    website = forms.CharField(required=False)  # honeypot, must stay empty

    def clean_pickup(self):
        return clean_address(self.cleaned_data["pickup"], "pickup point")

    def clean_destination(self):
        return clean_address(self.cleaned_data["destination"], "destination")

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

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Spam detected.")
        cleaned["ride_type"] = cleaned.get("ride_type") or BookingRequest.RIDE_NOW
        if cleaned["ride_type"] == BookingRequest.SCHEDULE:
            if not cleaned.get("scheduled_date"):
                self.add_error("scheduled_date", "Please choose a pickup date.")
            elif cleaned["scheduled_date"] < timezone.localdate():
                self.add_error("scheduled_date", "Pickup date can't be in the past.")
            if not cleaned.get("scheduled_time"):
                self.add_error("scheduled_time", "Please choose a pickup time.")
        else:
            cleaned["scheduled_date"] = cleaned["scheduled_time"] = None
        return cleaned
