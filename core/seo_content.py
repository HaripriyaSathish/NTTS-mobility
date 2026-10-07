"""Client SEO wording (NTTS_Mobility_SEO_Content), shared by seed_content and the data migrations."""

META_TITLE = "Book Taxi Online | Airport, Outstation & EV Cabs – New Track"
META_DESCRIPTION = (
    "Book a taxi online with verified drivers, transparent fares and safe rides. "
    "Choose airport, outstation, city, 7-seater and EV cab services with New Track."
)

SITE_SEO = {
    "meta_title": META_TITLE,
    "meta_description": META_DESCRIPTION,
    "og_title": META_TITLE,
    "og_description": META_DESCRIPTION,
}

# Section 01 – Hero. The H1 "Your Journey Starts with One Tap" is split over the
# dark first line and the green second line.
HERO_SEO = {
    "badge_text": "SMART CAB BOOKING",
    "title": "Your Journey Starts",
    "title_highlight": "with One Tap",
    "description": (
        "Book a taxi online for airport, outstation, one-way and local rides with verified chauffeurs, "
        "live tracking and transparent upfront fares. Enjoy safe, reliable rides with zero surge pricing."
    ),
    "card_title": "Book a Cab Instantly",
    "tab_labels": "Airport Cab\nOutstation\nOne Way\nHourly Rental",
    "button_text": "Book Taxi Now",
    "pricing_button_text": "Pricing Details",
}

# Section 02 – Featured Vehicles (fleet slider). Matched to the slides by tab name.
# **double stars** = words the client highlighted in bold.
FLEET_SLIDES_SEO = {
    "Luxe Sedan": {
        "badge_text": "ZERO-EMISSION LUXURY",
        "title": "NTTS Luxe Electric Sedan",
        "description": (
            "Experience premium electric cab travel with the NTTS Luxe Electric Sedan. Enjoy a quiet, "
            "comfortable ride with ambient lighting, ergonomic leather seating, onboard Wi-Fi and smooth "
            "zero-emission performance—perfect for city travel, airport transfers and premium cab bookings."
        ),
        "image_alt": "NTTS Luxe Electric Sedan",
        "specs": [("Cabin Space", "4 Seats"), ("Luggage", "2 Suitcases"),
                  ("Drive", "100% Electric"), ("Rating", "★ 4.98")],
    },
    "Smart City": {
        "badge_text": "SMART CITY TRAVEL",
        "title": "NTTS Urban Sedan",
        "description": (
            "Make your everyday travel easier with a **comfortable city taxi service** designed for work, "
            "shopping, appointments, and local travel. NTTS Urban Sedan provides **AC sedan cabs with "
            "professional drivers, transparent fares, and dependable city transportation** for hassle-free "
            "daily journeys."
        ),
        "image_alt": "NTTS Urban Sedan",
        "specs": [("Passenger Capacity", "4 Seats"), ("Luggage Capacity", "2 Bags"),
                  ("Travel Comfort", "Air Conditioned"), ("Customer Rating", "★ 4.90")],
    },
    "Exec SUV": {
        "badge_text": "EXECUTIVE LUXURY TRAVEL",
        "title": "NTTS Executive Grand SUV",
        "description": (
            "Travel in refined comfort with a **premium chauffeur-driven SUV** built for business trips, "
            "airport transfers, corporate travel, and special occasions. Enjoy a spacious 6-seat cabin, "
            "enhanced privacy, onboard Wi-Fi, convenient workspace features, and ample luggage capacity "
            "for a relaxed and productive journey."
        ),
        "image_alt": "NTTS Executive Grand SUV",
        "specs": [("Passenger Capacity", "6 Seats"), ("Luggage Capacity", "5 Suitcases"),
                  ("Privacy", "Grade A Tint"), ("Customer Rating", "★ 4.99")],
    },
}

# Stats row (under the fleet slider): new label under each number. Matched by the number.
STATS_SEO = {
    "10M+": "Safe Rides Completed",
    "4.9": "Average Customer Rating",
    "50+": "Cities & Metro Areas Served",
    "24/7": "Customer Support & Ride Assistance",
}
# Stat boxes that open a page when clicked (matched by the number)
STAT_LINKS = {
    "4.9": "https://share.google/EjcDuXGOV1B8110Hr",  # Google reviews
}

# Section 03 – Fleet & Rides (Choose Your Ride)
RIDES_SEO = {
    "title": "Choose Your Ride",
    "description": (
        "Explore reliable **cab booking and car rental options** for city travel, airport transfers, "
        "outstation trips, and group journeys. Choose from comfortable sedans, premium cars, spacious "
        "7-seater SUVs, and electric vehicles based on your travel needs, comfort, and budget."
    ),
    "side_badge_text": "100% Carbon-Neutral Fleet Options",
}

# Cards, matched by car type. Premium Sedan and Premium SUV were not in the client's doc,
# so their text is written in the same style (edit it in admin any time).
RIDE_CARDS_SEO = {
    "Compact Sedan": {
        "subtitle": "Affordable City & Daily Travel",
        "description": (
            "Comfortable AC sedan cabs for local trips, daily commutes, airport transfers, and convenient "
            "city travel with professional drivers."
        ),
        "features": "4 Seats\nAC Sedan\n2 Bags",
        "button_text": "Book Sedan",
    },
    "Premium Executive": {
        "subtitle": "Luxury Travel with Chauffeur",
        "description": (
            "Experience premium comfort with a luxury car with driver for business travel, airport "
            "transfers, special occasions, and executive journeys."
        ),
        "features": "Premium Car\nWi-Fi\nChauffeur Service",
        "button_text": "Book Premium",
    },
    "Spacious SUV": {
        "subtitle": "7-Seater Cab for Group Travel",
        "description": (
            "Travel together in a spacious SUV designed for 7-seater taxi booking, family trips, airport "
            "transfers, and outstation journeys with generous luggage space."
        ),
        "features": "6–7 Seats\nLarge Luggage\nDual-Zone AC",
        "button_text": "Book SUV",
    },
    "Electric EV Plus": {
        "subtitle": "Smart & Sustainable Electric Travel",
        "description": (
            "Choose an electric car rental option for comfortable, quiet, and eco-friendly journeys. "
            "Ideal for city travel and customers looking for a modern EV ride."
        ),
        "features": "4 Passengers\nZero Emission\nSilent Cabin",
        "button_text": "Book EV Plus",
    },
    "Premium Sedan": {
        "subtitle": "Spacious Sedan for Business Travel",
        "description": (
            "Ride in a roomy premium sedan with extra legroom and boot space, ideal for business trips, "
            "airport transfers, and comfortable city and outstation travel."
        ),
        "features": "4 Seats\nExtra Legroom\nSpacious Boot",
        "button_text": "Book Premium Sedan",
    },
    "Premium SUV": {
        "subtitle": "Family & Outstation SUV Travel",
        "description": (
            "Book a comfortable SUV cab for family trips, group travel, and outstation journeys, with "
            "6–7 seats and an optional roof carrier for extra luggage."
        ),
        "features": "6–7 Seats\nRoof Carrier\nOutstation Ready",
        "button_text": "Book Premium SUV",
    },
}

# Section 04 – How It Works, plus Section 05 (Fast & Reliable Cab Booking) = the green
# banner under the steps. The banner tag (99.98% DISPATCH UPTIME) is not in the doc, so it stays.
STEPS_SECTION_SEO = {
    "badge_text": "THE PROCESS",
    "title": "How to Book Your Cab in 3 Simple Steps",
    "description": (
        "Book your **cab or taxi online** in just three simple steps. Enter your pickup and destination, "
        "choose the right vehicle for your journey, and enjoy a comfortable ride with transparent pricing "
        "and reliable service."
    ),
    "banner_title": "Quick Driver Matching",
    "banner_text": (
        "Our smart booking system connects you with an available driver near your pickup location, helping "
        "you get a **cab for city travel, airport transfers, and outstation journeys** without unnecessary "
        "waiting."
    ),
}

# Steps, matched by position (1, 2, 3)
STEPS_SEO = {
    1: {
        "title": "Enter Your Pickup & Destination",
        "description": (
            "Enter your pickup location and destination to find the right **cab booking option** for your "
            "journey. Whether you need a city taxi, airport transfer, or outstation cab, get your ride "
            "details quickly."
        ),
        "highlight_text": (
            "**Live Location Detection –** Instantly identify your pickup point for faster and easier taxi booking."
        ),
    },
    2: {
        "title": "Select Your Cab & Fare",
        "description": (
            "Compare available vehicles, check the **cab fare**, and choose a ride that matches your travel "
            "needs. Select from sedan, SUV, premium, or electric vehicle options before confirming your booking."
        ),
        "highlight_text": (
            "**Transparent Upfront Pricing –** Know your estimated fare before confirming your **taxi booking**."
        ),
    },
    3: {
        "title": "Confirm & Enjoy Your Ride",
        "description": (
            "Confirm your booking and track your driver in real time. Share your trip details with your loved "
            "ones and complete your journey with convenient digital payment options."
        ),
        "highlight_text": (
            "**Live Ride Tracking –** Stay updated with your driver's location throughout the journey."
        ),
    },
}

# Section 06 – Safety. No tag above the heading (the client does not want the ISO line).
SAFETY_SEO = {
    "badge_text": "",
    "title": "Safe & Secure Cab Rides",
    "description": (
        "Your safety comes first on every **online cab booking**. From verified drivers and live GPS tracking "
        "to emergency assistance and accident protection, NTTS is designed to provide a secure travel "
        "experience for **local cab services, airport cab bookings, and outstation cab bookings**."
    ),
    "highlight_title": "NTTS Shield™ Active",
    "highlight_text": (
        "**Safety Support From Pickup to Drop-Off.** Every eligible NTTS journey is supported by continuous "
        "trip monitoring and safety measures, helping make your **taxi booking experience** more secure from "
        "start to finish."
    ),
    "highlight_tag": "24/7 Ride Monitoring",
}

# Feature cards, matched by position. Card 6 (Accident Protection) stays hidden: the client does not need it.
SAFETY_FEATURES_SEO = {
    1: {"title": "Verified Drivers", "subtitle": "Trusted Drivers for Every Journey",
        "description": "Every driver goes through identity, background, and driving-record verification before "
                       "accepting rides, helping you travel with greater confidence.",
        "check_text": "Verified Driver Screening"},
    2: {"title": "Live GPS Tracking", "subtitle": "Track Your Cab in Real Time",
        "description": "Stay connected throughout your journey with live GPS tracking. Share your ride details "
                       "with trusted contacts and know where your cab is during your trip.",
        "check_text": "Real-Time Ride Tracking"},
    3: {"title": "SOS Emergency Support", "subtitle": "Emergency Assistance When You Need It",
        "description": "Access quick emergency support during your ride with an SOS feature designed to help "
                       "connect you with the appropriate emergency response team.",
        "check_text": "24/7 Emergency Assistance"},
    4: {"title": "Private Communication", "subtitle": "Keep Your Phone Number Private",
        "description": "Your personal number stays protected through secure in-app communication, helping "
                       "maintain privacy between passengers and drivers.",
        "check_text": "Protected Contact Details"},
    5: {"title": "Two-Way Driver & Rider Ratings", "subtitle": "Better Accountability on Every Ride",
        "description": "Driver and passenger ratings help maintain service quality and encourage a professional "
                       "experience across every cab booking.",
        "check_text": "Verified Ratings & Reviews"},
    6: {"title": "Accident Protection", "subtitle": "Added Protection for Your Journey",
        "description": "Eligible rides include accident-related protection, giving passengers additional "
                       "confidence when using NTTS for airport taxi booking, local travel, and outstation trips.",
        "check_text": "Ride Protection Included", "is_active": False},
}

# Section 07 – Transparent Cab Fares (pricing)
PRICING_SEO = {
    "badge_text": "TRANSPARENT TARIFF",
    "title": "Simple & Transparent Cab Pricing",
    "description": (
        "Choose the right ride for your journey with **clear cab fares and upfront pricing**. Whether you need "
        "an affordable sedan for local travel, a premium executive car, an electric vehicle, or a spacious SUV, "
        "compare your options before confirming your **cab booking**."
    ),
    "highlights": "No Hidden Charges\nUpfront Fare\nFlexible Ride Options",
}

# Plans, matched by linked car. The client's doc was made from the old design, so its columns
# are matched by price: Executive Sedan ₹140 = Premium Sedan, NTTS Luxe EV ₹200 = Premium Executive.
# Premium Executive is a Mercedes E-Class (not electric), so the EV-only words are left out of it.
# Premium SUV was not in the doc, so its text is written in the same style.
PRICING_PLANS_SEO = {
    "Compact Sedan": {
        "subtitle": "Affordable Sedan Cab",
        "features": "₹15 per additional KM\n₹225 per additional hour\nUp to 4 Passengers\nFull Air Conditioning\nSpace for 2 Bags",
        "description": "A practical AC sedan taxi for daily commutes, local travel, airport transfers, "
                       "and short city journeys.",
        "button_text": "Select Sedan",
    },
    "Premium Sedan": {
        "subtitle": "Premium Executive Cab",
        "features": "₹16 per additional KM\n₹250 per additional hour\n4 Executive Seats\nBottled Water & Wi-Fi\nProfessional Chauffeur",
        "description": "Travel in comfort with a premium sedan featuring executive seating, Wi-Fi, bottled "
                       "water, and a professional chauffeur for business and special journeys.",
    },
    "Premium SUV": {
        "subtitle": "Family & Outstation SUV Cab",
        "features": "₹26 per additional KM\n₹250 per additional hour\n6–7 Passengers\nRoof Carrier Available\nIdeal for Outstation Trips",
        "description": "A comfortable SUV cab for family trips, group travel, and outstation journeys, with "
                       "an optional roof carrier for extra luggage.",
    },
    "Spacious SUV": {
        "subtitle": "Spacious SUV Cab",
        "features": "₹26 per additional KM\n₹250 per additional hour\n6–7 Passengers\nLarge Boot for 5+ Bags\nDual-Zone Climate Control",
        "description": "Need more room for passengers and luggage? Choose an SUV cab for family travel, group "
                       "journeys, airport transfers, and longer trips.",
        "button_text": "Select SUV",
    },
    "Premium Executive": {
        "subtitle": "Luxury Executive Car",
        "features": "₹90 per additional KM\n₹250 per additional hour\n4 Luxury Seats\nProfessional Chauffeur\nPriority Pickup & Concierge",
        "description": "Choose a premium luxury car rental option for a quiet, comfortable ride with priority "
                       "pickup and enhanced travel comfort.",
    },
}

# Section 08 – Rider Experiences (testimonials heading). The reviews themselves are unchanged.
TESTIMONIALS_SECTION_SEO = {
    "badge_text": "VERIFIED RIDERS",
    "title": "Chosen for the Journey, Trusted for the Ride",
    "description": (
        "A great ride is more than getting from one place to another. NTTS Mobility brings together **reliable "
        "cab booking, professional drivers, comfortable vehicles, and dependable service** for everyday travel, "
        "airport transfers, business trips, and outstation journeys."
    ),
}

# Section 10 – FAQ. These 6 replace the earlier questions (which are hidden, not deleted).
# The client's doc used the old car names and prices, so those parts are updated to the
# current cars (Premium Sedan ₹140, Premium SUV ₹230, Premium Executive ₹200, Spacious SUV ₹260).
# Also left out: the mobile app (there is none), electric cabs and accident protection (not offered).
FAQ_ITEMS_SEO = [
    ("How do I book a taxi online with New Track?",
     "Use the New Track website. Enter your pickup and destination, choose a Compact Sedan, Premium Sedan, "
     "Premium Executive or SUV, check the upfront fare, and confirm. You can then track your driver in real time "
     "and pay digitally."),
    ("How much does a New Track cab cost, and is there surge pricing?",
     "New Track shows the fare upfront before you confirm, with zero surge pricing and no hidden charges. Local "
     "packages start at 4 Hrs / 40 Km: Compact Sedan ₹1,400 (₹15 per extra km), Premium Sedan ₹1,500 (₹16 per km), "
     "Premium SUV and Spacious SUV ₹3,000 (₹26 per km), and Premium Executive ₹5,000 (₹90 per km). Fuel and "
     "driver allowance are included; taxes are extra."),
    ("Can I book an airport cab with New Track?",
     "Yes. Select the Airport Cab tab, enter your pickup and drop, and choose a vehicle that fits your luggage. "
     "Sedans carry 2 bags, the Executive Grand SUV carries 5 suitcases, and the Spacious SUV has a large boot for "
     "5+ bags. Verified chauffeurs and live tracking are included."),
    ("Can I book an outstation or one-way cab?",
     "Yes. New Track offers Outstation, One Way and Hourly Rental bookings. You can choose a sedan, premium "
     "executive car or SUV for longer trips and see the fare before you confirm."),
    ("What types of cabs can I book, including 7-seater?",
     "New Track offers five options: Compact Sedan (4 seats), Premium Sedan (extra legroom and boot space), "
     "Premium SUV (6 to 7 seats, optional roof carrier), Spacious SUV (6 to 7 seats, large boot, dual-zone AC) and "
     "Premium Executive (chauffeur-driven, Wi-Fi). Choose based on your group size and luggage."),
    ("Is New Track safe, and are the drivers verified?",
     "Yes. Every driver goes through identity, background and driving-record verification before accepting rides. "
     "Each trip includes live GPS tracking, an in-app SOS button, 24/7 ride monitoring, private in-app calling that "
     "hides your phone number, and two-way driver and rider ratings."),
]

# Section 11 – Footer (text under the logo)
FOOTER_SEO = {
    "tagline": "Safe & Reliable Mobility for the Modern City",
    "about_text": (
        "New Track makes **online cab booking** simple, comfortable, and secure. Book **city taxis, airport cabs, "
        "outstation rides, and intercity travel** with verified drivers, real-time GPS tracking, emergency "
        "assistance, and transparent fares."
    ),
    "highlights": "Safe Rides\nVerified Drivers\nLive GPS Tracking\nTransparent Pricing",
}
