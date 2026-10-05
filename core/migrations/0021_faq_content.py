"""Add the FAQ section (it replaces the app download banner) with its starting questions."""
from django.db import migrations

FAQ_SECTION = {'is_active': True,
 'badge_text': 'FAQ',
 'title': 'Frequently Asked Questions',
 'description': 'Everything you need to know about booking, fares and safety with New Track.',
 'show_help_box': True,
 'help_title': 'Still have questions?',
 'help_text': 'Our help desk team is happy to help you plan your ride.',
 'help_button_text': 'Call Help Desk'}

FAQ_ITEMS = [('How do I book a ride?',
  'Tap “Book a Ride”, enter your pickup city and destination, choose a car and add your name, mobile number '
  'and email. Our team will call you shortly to confirm the booking.'),
 ('How soon will my car arrive?',
  'For instant bookings, your car usually arrives within 30–40 minutes. If you need it at a fixed time, use '
  'the Schedule option while booking.'),
 ('Can I book a ride in advance?',
  'Yes. Choose “Schedule” in the booking form and pick your pickup date and time.'),
 ('How is the fare calculated?',
  'Each car type has a base fare plus a per-kilometre rate, shown in the Pricing section. The fare is shared '
  'with you upfront before you confirm.'),
 ('Is there any surge pricing?',
  'No. We never apply surge pricing, so you pay the same fair rate at any time of the day.'),
 ('Can I cancel my booking?',
  'Yes. Cancellation is free within 3 minutes of booking. After that, please call our help desk and we will '
  'assist you.'),
 ('Are your drivers verified?',
  'Yes. Every driver goes through background and driving record checks before their first trip.'),
 ('Do you offer airport transfers and outstation trips?',
  'Yes. Along with daily city rides, we offer airport pickups and drops and outstation trips. Book online or '
  'call our help desk to plan your trip.')]


def add_faq(apps, schema_editor):
    FAQSection = apps.get_model("core", "FAQSection")
    FAQItem = apps.get_model("core", "FAQItem")
    if not FAQSection.objects.filter(pk=1).exists():
        FAQSection.objects.create(pk=1, **FAQ_SECTION)
    if not FAQItem.objects.exists():
        for i, (question, answer) in enumerate(FAQ_ITEMS, start=1):
            FAQItem.objects.create(question=question, answer=answer, order=i)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0020_faq_replaces_app_download"),
    ]

    operations = [
        migrations.RunPython(add_faq, migrations.RunPython.noop),
    ]
