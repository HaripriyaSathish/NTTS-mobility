"""
Booking popup: the 3 trip tabs (Airport Transfer / Local – Hourly Rentals / Outstation).
Used by seed_content and by migration 0031, so keep these names.

Local – Hourly Rentals prices are the client's real rates (ONLINE RATE 26-27, "Local" sheet).
Airport and Outstation prices are still SAMPLE prices until the client shares them.
All prices are edited any time in admin: "3. Booking Popup – Prices".
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

# Local – Hourly Rentals terms, one point per line (client's sheet: "Terms & Conditions")
LOCAL_TERMS = "Includes Fuel, Driver Allowance\nTaxes excluded"

# Passenger seats per car (Outstation hides cars that are too small for "No of Pax")
SEATS = {
    "Compact Sedan": 4,
    "Premium Sedan": 4,
    "Premium SUV": 7,
    "Spacious SUV": 7,
    "Premium Executive": 4,
}

# Local – Hourly Rentals packages, in display order
RENTAL_PACKAGES = ["4 Hrs / 40 Km", "6 Hrs / 60 Km", "8 Hrs / 80 Km", "10 Hrs / 100 Km", "12 Hrs / 120 Km"]


def _local(*prices):
    """Local package prices, in RENTAL_PACKAGES order."""
    return dict(zip(RENTAL_PACKAGES, (Decimal(p) for p in prices)))


# Prices per car: (price, text after price, extra km rate, extra hour rate)
_P = Decimal
TRIP_RATES = {
    "Compact Sedan": {
        "airport": (_P("1200"), "fixed", _P("14"), None),
        "local": _local("1400", "2000", "2400", "2750", "3000"),
        "local_extra": (_P("15"), _P("225")),
        "outstation": (_P("3500"), "per day (250 Km)", _P("14"), None),
    },
    "Premium Sedan": {
        "airport": (_P("1500"), "fixed", _P("18"), None),
        "local": _local("1500", "2250", "3000", "3750", "4500"),
        "local_extra": (_P("16"), _P("250")),
        "outstation": (_P("4500"), "per day (250 Km)", _P("18"), None),
    },
    "Premium SUV": {
        "airport": (_P("2000"), "fixed", _P("22"), None),
        "local": _local("3000", "4500", "6000", "7500", "6337"),
        "local_extra": (_P("26"), _P("250")),
        "outstation": (_P("5500"), "per day (250 Km)", _P("22"), None),
    },
    "Spacious SUV": {
        "airport": (_P("2500"), "fixed", _P("28"), None),
        "local": _local("3000", "4500", "6000", "7500", "6337"),
        "local_extra": (_P("26"), _P("250")),
        "outstation": (_P("7000"), "per day (250 Km)", _P("28"), None),
    },
    "Premium Executive": {
        "airport": (_P("3500"), "fixed", _P("24"), None),
        "local": _local("5000", "4500", "6000", "7500", "6337"),
        "local_extra": (_P("90"), _P("250")),
        "outstation": (_P("6000"), "per day (250 Km)", _P("24"), None),
    },
}


def starting_price(car_name):
    """The car's cheapest Local package (4 Hrs / 40 Km) – shown as the base price on the
    Fleet & Rides cards and the Pricing plans (client's sheet ONLINE RATE 26-27)."""
    return TRIP_RATES[car_name]["local"][RENTAL_PACKAGES[0]]


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


# Pickup / Drop suggestions in the booking popup (Chennai). Edited in admin: "3. Booking Popup".
# Only letters, numbers and , . - / & ( ) ' – the same characters the address boxes accept.
CHENNAI_LOCATIONS = [
    # Airport, railway stations, bus terminals
    "Chennai International Airport (MAA), Meenambakkam",
    "Chennai Airport, Domestic Terminal",
    "Chennai Airport, International Terminal",
    "Chennai Central Railway Station (MGR Central)",
    "Chennai Egmore Railway Station",
    "Tambaram Railway Station",
    "Chennai Beach Railway Station",
    "Perambur Railway Station",
    "Guindy Railway Station",
    "Mambalam Railway Station",
    "Avadi Railway Station",
    "Tiruvallur Railway Station",
    "Chengalpattu Railway Station",
    "Koyambedu CMBT Bus Terminus",
    "Kilambakkam Bus Terminus (KCBT)",
    "Madhavaram Mofussil Bus Terminus",
    "Chennai Port",
    # Central Chennai
    "Anna Salai (Mount Road)", "Egmore", "Nungambakkam", "T. Nagar", "Teynampet", "Alwarpet", "Mylapore",
    "Mandaveli", "Raja Annamalaipuram (R.A. Puram)", "Gopalapuram", "Royapettah", "Triplicane", "Chepauk",
    "Thousand Lights", "Kodambakkam", "West Mambalam", "Ashok Nagar", "K.K. Nagar", "Vadapalani", "Saligramam",
    "Virugambakkam", "Valasaravakkam", "Chetpet", "Kilpauk", "Purasawalkam", "Aminjikarai", "Shenoy Nagar",
    "Anna Nagar", "Anna Nagar West", "Anna Nagar East", "Arumbakkam", "Choolaimedu", "Nandanam", "Saidapet",
    "CIT Nagar", "Abhiramapuram", "Santhome", "George Town", "Parrys Corner", "Park Town", "Sowcarpet",
    "Royapuram", "Washermanpet", "Tondiarpet", "Vepery", "Periamet", "Pudupet", "Chintadripet",
    # South Chennai & OMR / ECR
    "Adyar", "Besant Nagar", "Thiruvanmiyur", "Kotturpuram", "Guindy", "Velachery", "Taramani", "Perungudi",
    "Kandanchavadi", "Thoraipakkam", "Karapakkam", "Sholinganallur", "Semmancheri", "Navalur", "Siruseri",
    "Kelambakkam", "Padur", "Egattur", "Medavakkam", "Pallikaranai", "Madipakkam", "Nanganallur",
    "Keelkattalai", "Kovilambakkam", "Jaladampet", "Nanmangalam", "Puzhuthivakkam", "Ullagaram", "Adambakkam",
    "Alandur", "St. Thomas Mount", "Meenambakkam", "Pallavaram", "Chromepet", "Hasthinapuram", "Tambaram",
    "East Tambaram", "West Tambaram", "Selaiyur", "Sembakkam", "Rajakilpakkam", "Perungalathur", "Vandalur",
    "Urapakkam", "Guduvanchery", "Potheri", "Kattankulathur", "Maraimalai Nagar", "Singaperumal Koil",
    "Chengalpattu", "Neelankarai", "Palavakkam", "Kottivakkam", "Injambakkam", "Uthandi", "Akkarai",
    "Muttukadu", "Kovalam", "Mamallapuram (Mahabalipuram)", "Kalpakkam",
    # West Chennai
    "Porur", "Ramapuram", "Iyyappanthangal", "Mugalivakkam", "Manapakkam", "Gerugambakkam",
    "Kundrathur", "Mangadu", "Poonamallee", "Kattupakkam", "Thirumazhisai", "Nazarethpettai", "Sriperumbudur",
    "Oragadam", "Irungattukottai", "Mevalurkuppam", "Vanagaram", "Maduravoyal", "Alapakkam", "Nerkundram",
    "Koyambedu", "Thirumangalam", "Mogappair", "Mogappair East", "Mogappair West", "Padi", "Korattur",
    "Ambattur", "Ambattur Industrial Estate", "Pattabiram", "Avadi", "Thirumullaivoyal", "Thiruverkadu",
    "Paruthipattu", "Tiruvallur",
    # North Chennai
    "Perambur", "Kolathur", "Villivakkam", "Ayanavaram", "Otteri", "Vyasarpadi", "Kodungaiyur", "Madhavaram",
    "Puzhal", "Red Hills", "Retteri", "Moolakadai", "Manali", "Tiruvottiyur", "Ennore", "Minjur", "Ponneri",
    "Thiruninravur",
    # IT parks, business hubs
    "Tidel Park, Taramani", "DLF IT Park, Manapakkam", "DLF Cybercity, Porur", "Olympia Tech Park, Guindy",
    "RMZ Millenia Business Park, Perungudi", "Ascendas IT Park (International Tech Park), Taramani",
    "SIPCOT IT Park, Siruseri", "ELCOT SEZ, Sholinganallur", "Mahindra World City, Chengalpattu",
    "Chennai One SEZ, Thoraipakkam", "Ramanujan IT City, Taramani", "World Trade Center, Perungudi",
    "Guindy Industrial Estate", "SIPCOT Sriperumbudur", "SIPCOT Oragadam",
    # Malls, landmarks, beaches
    "Phoenix MarketCity, Velachery", "Palladium Mall, Velachery", "Express Avenue Mall, Royapettah",
    "VR Chennai, Anna Nagar", "Forum Vijaya Mall, Vadapalani", "Nexus Vijaya Mall, Vadapalani",
    "Marina Mall, Egattur", "Spencer Plaza, Anna Salai", "Ampa Skywalk, Aminjikarai", "Pothys, T. Nagar",
    "Ranganathan Street, T. Nagar", "Pondy Bazaar, T. Nagar", "Marina Beach", "Elliot's Beach, Besant Nagar",
    "Kapaleeshwarar Temple, Mylapore", "Parthasarathy Temple, Triplicane", "Santhome Cathedral",
    "Vadapalani Murugan Temple", "Ashtalakshmi Temple, Besant Nagar", "Fort St. George",
    "Valluvar Kottam, Nungambakkam", "Guindy National Park", "Arignar Anna Zoological Park, Vandalur",
    "VGP Universal Kingdom, Injambakkam", "MGM Dizzee World, Muttukadu", "Dakshinachitra, Muttukadu",
    "Chennai Trade Centre, Nandambakkam", "MA Chidambaram Stadium, Chepauk", "Jawaharlal Nehru Stadium, Periamet",
    # Hospitals
    "Apollo Hospitals, Greams Road", "Apollo Hospital, OMR", "Fortis Malar Hospital, Adyar",
    "MIOT International, Manapakkam", "Kauvery Hospital, Alwarpet", "Sri Ramachandra Hospital, Porur",
    "Gleneagles Global Health City, Perumbakkam", "SIMS Hospital, Vadapalani", "Rajiv Gandhi Government General Hospital",
    "Sankara Nethralaya, Nungambakkam", "Vijaya Hospital, Vadapalani", "Prashanth Hospital, Velachery",
    "Dr. Rela Institute, Chromepet", "Kilpauk Medical College Hospital", "Stanley Medical College Hospital",
    # Colleges
    "IIT Madras, Guindy", "Anna University, Guindy", "SRM University, Kattankulathur", "VIT Chennai, Kelambakkam",
    "Loyola College, Nungambakkam", "Madras Christian College, Tambaram", "Sathyabama University, Semmancheri",
    "Hindustan University, Padur", "SSN College, Kalavakkam", "Presidency College, Chepauk",
]
