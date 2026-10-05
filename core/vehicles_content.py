"""
The client's vehicle types (booking popup cars + Fleet & Rides cards).
Used by seed_content and by migration 0028, so keep these names.

"old_names" lets the migration rename an existing record (keeping its uploaded photo and the
pricing plan linked to it) instead of creating a duplicate.
"""
from decimal import Decimal

# Booking popup – car options
VEHICLES = [
    {"name": "Compact Sedan", "old_names": [], "button_name": "Compact Sedan",
     "details": "Dzire Tour, Aura, Amaze · 4+1",
     "base_price": Decimal("80"), "badge_text": "", "is_default": False, "is_active": True, "order": 1},
    {"name": "Premium Sedan", "old_names": ["Executive Sedan"], "button_name": "Premium Sedan",
     "details": "Maruti Ciaz · 4+1",
     "base_price": Decimal("140"), "badge_text": "", "is_default": False, "is_active": True, "order": 2},
    {"name": "Premium SUV", "old_names": [], "button_name": "Premium SUV",
     "details": "Innova Crysta · 6+1 / 7+1",
     "base_price": Decimal("230"), "badge_text": "", "is_default": False, "is_active": True, "order": 3},
    {"name": "Spacious SUV", "old_names": [], "button_name": "Spacious SUV",
     "details": "Innova Hycross · 6+1 / 7+1",
     "base_price": Decimal("260"), "badge_text": "", "is_default": False, "is_active": True, "order": 4},
    {"name": "Premium Executive", "old_names": ["NTTS Luxe EV"], "button_name": "Premium Executive",
     "details": "Mercedes-Benz E-Class",
     "base_price": Decimal("200"), "badge_text": "", "is_default": False, "is_active": True, "order": 5},
]

# Fleet & Rides – cards ("booking_car" = the car above that the card's button picks)
RIDE_OPTIONS = [
    {"name": "Compact Sedan", "old_names": [], "base_price": Decimal("80"), "badge_text": "",
     "description": "Swift Dzire Tour, Hyundai Aura or Honda Amaze – comfortable AC sedans for city rides "
                    "and daily commutes.",
     "features": "Dzire Tour / Aura / Amaze\n4+1 Seating\nFull AC",
     "button_text": "Book Sedan", "booking_car": "Compact Sedan", "is_featured": False, "is_active": True, "order": 1},
    {"name": "Premium Sedan", "old_names": [], "base_price": Decimal("140"), "badge_text": "",
     "description": "Maruti Ciaz with extra legroom and boot space, ideal for business trips and "
                    "airport transfers.",
     "features": "Maruti Ciaz\n4+1 Seating\nSpacious Boot",
     "button_text": "Book Premium Sedan", "booking_car": "Premium Sedan", "is_featured": False, "is_active": True, "order": 2},
    {"name": "Premium SUV", "old_names": [], "base_price": Decimal("230"), "badge_text": "",
     "description": "Toyota Innova Crysta for family trips, group travel and outstation journeys, "
                    "available with or without a roof carrier.",
     "features": "Innova Crysta\n6+1 / 7+1 Seating\nWith / Without Carrier",
     "button_text": "Book Premium SUV", "booking_car": "Premium SUV", "is_featured": False, "is_active": True, "order": 3},
    {"name": "Spacious SUV", "old_names": [], "base_price": Decimal("260"), "badge_text": "FAMILY & GROUP",
     "description": "Toyota Innova Hycross – a roomy, modern SUV for groups and families who want "
                    "extra comfort.",
     "features": "Innova Hycross\n6+1 / 7+1 Seating\nSpacious Cabin",
     "button_text": "Book SUV", "booking_car": "Spacious SUV", "is_featured": False, "is_active": True, "order": 4},
    {"name": "Premium Executive", "old_names": [], "base_price": Decimal("200"), "badge_text": "TOP TIER",
     "description": "Mercedes-Benz E-Class with professional chauffeurs for VIP, executive and "
                    "business travel.",
     "features": "Mercedes-Benz E-Class\nProfessional Chauffeur\nPriority Pickup",
     "button_text": "Book Executive", "booking_car": "Premium Executive", "is_featured": True, "is_active": True, "order": 5},
]

# No longer offered: hidden (not deleted, so its uploaded photo is kept in admin)
HIDDEN_RIDE_CARDS = ["Electric EV Plus"]
