"""
Booking popup: the 3 trip tabs (Airport Transfer / Local – Hourly Rentals / Outstation).
Used by seed_content and by migration 0031, so keep these names.

The prices below are SAMPLE prices until the client shares the real packages.
They are edited any time in admin: "3. Booking Popup – Prices".
"""
from decimal import Decimal

# Popup wording (client's words: "Book Instantly", "Pickup at", "Drop at", "No of Days", "No of Pax")
BOOKING_TEXT = {
    "title": "Book Instantly",
    "airport_tab_label": "Airport Transfer",
    "local_tab_label": "Local – Hourly Rentals",
    "outstation_tab_label": "Outstation",
    "pickup_label": "Pickup at",
    "pickup_placeholder": "Enter pickup address",
    "destination_label": "Drop at",
    "destination_placeholder": "Enter drop address or airport",
    "schedule_date_label": "Pickup Date",
    "schedule_time_label": "Pickup Time",
    "flight_label": "Flight Number",
    "flight_placeholder": "e.g. 6E 2134",
    "days_label": "No of Days",
    "pax_label": "No of Pax",
    "package_heading": "Select the Package",
    "vehicle_heading": "Type of Vehicle",
    "nearby_suffix": "options",
    "no_cars_text": "No cars are available for this trip yet. Please call us to book.",
}

# Passenger seats per car (Outstation hides cars that are too small for "No of Pax")
SEATS = {
    "Compact Sedan": 4,
    "Premium Sedan": 4,
    "Premium SUV": 7,
    "Spacious SUV": 7,
    "Premium Executive": 4,
}

# Local – Hourly Rentals packages, in display order
RENTAL_PACKAGES = ["4 Hrs / 40 Km", "8 Hrs / 80 Km", "12 Hrs / 120 Km"]

# Sample prices per car: (price, text after price, extra km rate, extra hour rate)
_P = Decimal
TRIP_RATES = {
    "Compact Sedan": {
        "airport": (_P("1200"), "fixed", _P("14"), None),
        "local": {"4 Hrs / 40 Km": _P("1100"), "8 Hrs / 80 Km": _P("2000"), "12 Hrs / 120 Km": _P("2800")},
        "local_extra": (_P("14"), _P("150")),
        "outstation": (_P("3500"), "per day (250 Km)", _P("14"), None),
    },
    "Premium Sedan": {
        "airport": (_P("1500"), "fixed", _P("18"), None),
        "local": {"4 Hrs / 40 Km": _P("1400"), "8 Hrs / 80 Km": _P("2600"), "12 Hrs / 120 Km": _P("3600")},
        "local_extra": (_P("18"), _P("200")),
        "outstation": (_P("4500"), "per day (250 Km)", _P("18"), None),
    },
    "Premium SUV": {
        "airport": (_P("2000"), "fixed", _P("22"), None),
        "local": {"4 Hrs / 40 Km": _P("1800"), "8 Hrs / 80 Km": _P("3200"), "12 Hrs / 120 Km": _P("4500")},
        "local_extra": (_P("22"), _P("250")),
        "outstation": (_P("5500"), "per day (250 Km)", _P("22"), None),
    },
    "Spacious SUV": {
        "airport": (_P("2500"), "fixed", _P("28"), None),
        "local": {"4 Hrs / 40 Km": _P("2200"), "8 Hrs / 80 Km": _P("3900"), "12 Hrs / 120 Km": _P("5400")},
        "local_extra": (_P("28"), _P("300")),
        "outstation": (_P("7000"), "per day (250 Km)", _P("28"), None),
    },
    "Premium Executive": {
        "airport": (_P("3500"), "fixed", _P("24"), None),
        "local": {"4 Hrs / 40 Km": _P("4000"), "8 Hrs / 80 Km": _P("7500"), "12 Hrs / 120 Km": _P("10500")},
        "local_extra": (_P("24"), _P("600")),
        "outstation": (_P("6000"), "per day (250 Km)", _P("24"), None),
    },
}


def rate_rows(car_name):
    """All TripRate values for one car as dicts: trip_type, package (name or None), price…"""
    data = TRIP_RATES.get(car_name)
    if not data:
        return []
    rows = []
    for trip in ("airport", "outstation"):
        price, suffix, km, hour = data[trip]
        rows.append({"trip_type": trip, "package": None, "price": price, "price_suffix": suffix,
                     "extra_km_rate": km, "extra_hour_rate": hour})
    km, hour = data["local_extra"]
    for package, price in data["local"].items():
        rows.append({"trip_type": "local", "package": package, "price": price, "price_suffix": "",
                     "extra_km_rate": km, "extra_hour_rate": hour})
    return rows
