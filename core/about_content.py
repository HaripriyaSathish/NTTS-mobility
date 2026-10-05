"""
About Us wording supplied by the client (founder story, services, mission/vision, values).
Used by seed_content and by migration 0027, so keep these names.
"""

ABOUT = {
    "is_active": True,
    "badge_text": "ABOUT US",
    "title": "Our Founder & About NTTS",
    "description": (
        "Founded by Mr. Jagadeesan in 2004 as New Track Travels Services, the company has grown from a humble "
        "beginning into a powerhouse in corporate mobility.\n"
        "Now registered as NTTS Mobility Private Limited, it is a trusted name in corporate car rentals, fleet "
        "management, and business travel built on reliability, transparency and professionalism in every mile."
    ),
    "image_alt": "NTTS Mobility corporate fleet",
    "services_heading": "Our Fleet Services",
    "services": "\n".join([
        "Corporate Car Hire & Chauffeur Services",
        "Event & Large-Group Transportation",
        "VIP & Executive Mobility",
        "Employee Transportation Solutions",
        "Luxury Cars for Business Travel",
        "Bus Rentals for Corporates & Events",
    ]),
    "mission_title": "Mission",
    "mission_text": (
        "Our mission is to provide reliable and efficient corporate mobility solutions that empower businesses "
        "to thrive through seamless transportation experiences."
    ),
    "vision_title": "Vision",
    "vision_text": (
        "We envision a future where mobility is effortless, and every journey reflects our commitment to "
        "excellence and customer satisfaction in corporate transport services."
    ),
    "why_title": "Why NTTS",
    "why_text": (
        "NTTS stands out through our dedicated professionalism, commitment to punctuality, and advanced fleet "
        "management, ensuring optimum service quality and peace of mind for our clients."
    ),
    "values_heading": "Our Value Add",
}

ABOUT_VALUES = [
    {"icon": "award", "title": "Professionalism", "order": 1,
     "text": "At NTTS Mobility, professionalism drives every interaction, reflecting our commitment to "
             "excellence and service quality."},
    {"icon": "clock", "title": "Punctuality", "order": 2,
     "text": "We ensure punctuality in every operation, guaranteeing timely service and lasting trust."},
    {"icon": "target", "title": "Precision", "order": 3,
     "text": "We combine precision, technology, and planning to deliver seamless, tailored mobility solutions "
             "for every corporate need."},
]
