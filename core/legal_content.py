"""
Starting text for the Privacy Policy / Terms popups and the footer Support & Legal links.
Used by seed_content and by migration 0023, so keep these names.
"""
LEGAL_PAGES = [
    {
        "title": "Privacy Policy",
        "slug": "privacy-policy",
        "intro": (
            "This policy explains what information New Track (NTTS Car Rentals) collects when you use "
            "our website and book a ride, and how we use and protect it."
        ),
        "content": "\n".join([
            "# Information we collect",
            "Your name, mobile number and email address when you book a ride.",
            "Ride details such as pickup city, destination, date, time and the car type you choose.",
            "Basic technical details such as your IP address, used only to keep the website secure.",
            "# How we use your information",
            "To confirm your booking and contact you about your ride.",
            "To share the pickup details needed by the driver assigned to your trip.",
            "To send booking confirmations and reply to your questions.",
            "To improve our service and keep our riders and drivers safe.",
            "# Sharing your information",
            "We never sell or rent your personal information to anyone.",
            "Your details are shared only with the driver handling your trip, or when required by law.",
            "# Keeping your data safe",
            "Your information is stored securely and only authorised staff can access it.",
            "We keep booking records only as long as needed for service, accounts and legal requirements.",
            "# Your choices",
            "You can ask us to correct or delete your details at any time by contacting our help desk.",
            "# Contact us",
            "For any privacy questions, email info@newtrackindia.com or call our help desk on 9543024365.",
        ]),
        "order": 1,
    },
    {
        "title": "Terms of Transit",
        "slug": "terms-of-transit",
        "intro": "By booking a ride with New Track (NTTS Car Rentals), you agree to the following terms.",
        "content": "\n".join([
            "# Bookings",
            "A booking is confirmed only after our team contacts you on the mobile number you shared.",
            "Please enter the correct pickup, destination and contact details so we can reach you on time.",
            "# Arrival time",
            "For instant rides, the car usually arrives within 30–40 minutes.",
            "Arrival time may change due to traffic, weather or road conditions.",
            "# Fares and payment",
            "Fares are based on the base fare and per-kilometre rate of the car you choose, shared upfront before your trip.",
            "We do not apply surge pricing.",
            "Toll, parking and state permit charges on your route, if any, are paid by the rider.",
            "# Cancellations",
            "Cancellation is free within 3 minutes of booking.",
            "For cancellations after that, please call our help desk.",
            "# During your ride",
            "Please wear your seat belt at all times.",
            "Smoking, alcohol and illegal items are not allowed in the car.",
            "Any damage to the car caused by the rider may be charged.",
            "The driver may end the trip if the rider's behaviour puts anyone's safety at risk.",
            "# Luggage and belongings",
            "Carry luggage that fits the boot space of the car you book.",
            "Please check your belongings before leaving the car. We will help you find lost items, but we are not responsible for them.",
            "# Safety",
            "All our drivers are verified before their first trip.",
            "If you face any problem during your ride, call our help desk immediately.",
            "# Changes to these terms",
            "We may update these terms from time to time. The latest version is always shown here.",
        ]),
        "order": 2,
    },
]

SUPPORT_LINKS = [
    ("FAQs", "#faq"),
    ("Book a Ride", "#book"),
    ("Rider Reviews", "#testimonials"),
    ("Contact Us", "#contact"),
]
LEGAL_LINKS = [
    ("Privacy Policy", "#privacy-policy"),
    ("Terms of Transit", "#terms-of-transit"),
]
