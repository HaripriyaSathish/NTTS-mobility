"""
Pricing plans for the client's 5 vehicle types (price comes from the linked car).
Used by seed_content and by migration 0029, so keep these names.

"old_titles" lets the migration rename an existing plan instead of creating a duplicate.
"""

PRICING_PLANS = [
    {"title": "COMPACT SEDAN", "old_titles": [], "color": "dark", "icon": "sedan", "car": "Compact Sedan",
     "badge_text": "", "is_featured": False, "order": 1,
     "features": "₹14 per additional KM\nSwift Dzire Tour / Aura / Amaze\n4+1 Seating, Full AC\nBoot Space for 2 Bags",
     "button_text": "Select Sedan"},
    {"title": "PREMIUM SEDAN", "old_titles": ["EXECUTIVE SEDAN"], "color": "navy", "icon": "executive", "car": "Premium Sedan",
     "badge_text": "", "is_featured": False, "order": 2,
     "features": "₹18 per additional KM\nMaruti Ciaz\n4+1 Seating\nExtra Legroom & Boot Space",
     "button_text": "Select Premium Sedan"},
    {"title": "PREMIUM SUV", "old_titles": [], "color": "navy", "icon": "suv", "car": "Premium SUV",
     "badge_text": "", "is_featured": False, "order": 3,
     "features": "₹22 per additional KM\nToyota Innova Crysta\n6+1 / 7+1 Seating\nWith / Without Carrier",
     "button_text": "Select Premium SUV"},
    {"title": "SPACIOUS SUV", "old_titles": ["SPACIOUS SUV / XL"], "color": "dark", "icon": "suv", "car": "Spacious SUV",
     "badge_text": "", "is_featured": False, "order": 4,
     "features": "₹28 per additional KM\nToyota Innova Hycross\n6+1 / 7+1 Seating\nSpacious Cabin",
     "button_text": "Select SUV"},
    {"title": "PREMIUM EXECUTIVE", "old_titles": ["NTTS LUXE EV"], "color": "green", "icon": "ev", "car": "Premium Executive",
     "badge_text": "TOP TIER", "is_featured": True, "order": 5,
     "features": "₹24 per additional KM\nMercedes-Benz E-Class\nProfessional Chauffeur\nPriority Pickup & Concierge",
     "button_text": "Select Executive"},
]
