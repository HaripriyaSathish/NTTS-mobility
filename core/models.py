from cloudinary.models import CloudinaryField
from django.db import models
from django.utils import timezone


class SMTPSettings(models.Model):
    host = models.CharField("Mail server", max_length=255, default="smtp.gmail.com",
                            help_text="For Gmail keep smtp.gmail.com")
    port = models.PositiveIntegerField(default=587, help_text="Gmail: 587 (with TLS) or 465 (with SSL)")
    use_tls = models.BooleanField("Use TLS", default=True)
    use_ssl = models.BooleanField("Use SSL", default=False, help_text="Only for port 465. Don't tick both TLS and SSL.")
    username = models.CharField("Login email", max_length=255, help_text="The email account that sends the mails")
    password = models.CharField("App password", max_length=255, help_text="For Gmail, create an App Password")
    from_email = models.CharField("Sender name & email", max_length=255,
                                  help_text="e.g. NTTS Mobility <info@nttsmobility.com>")
    receiver_email = models.EmailField("Send booking alerts to", help_text="New ride requests are emailed here")
    is_active = models.BooleanField("Emails on", default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Email Settings (SMTP)"
        verbose_name_plural = "Email Settings (SMTP)"

    def __str__(self):
        return f"{self.username} ({self.host})"

    def save(self, *args, **kwargs):
        self.pk = 1  # only one record allowed
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        return cls.objects.filter(pk=1, is_active=True).first()


# ---------------------------------------------------------------------------
# Base helpers
# ---------------------------------------------------------------------------
class SingletonModel(models.Model):
    """A model that only ever has one row (pk=1)."""

    updated_at = models.DateTimeField("Last updated", auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        return cls.objects.filter(pk=1).first()


class OrderedModel(models.Model):
    order = models.PositiveIntegerField("Position", default=0, help_text="1 shows first, 2 next…")
    is_active = models.BooleanField("Show on website", default=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


def lines(text):
    """Split a newline-separated admin field into a clean list."""
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# 1. Website settings: logo, menu, SEO
# ---------------------------------------------------------------------------
class SiteSettings(SingletonModel):
    # Branding
    site_name = models.CharField("Business name", max_length=100, default="NTTS Mobility")
    logo = CloudinaryField("Logo", blank=True, null=True, folder="ntts/branding")
    logo_alt = models.CharField("Logo description", max_length=150, default="NTTS Mobility",
                                help_text="Read by Google and screen readers")
    favicon = CloudinaryField("Browser tab icon", blank=True, null=True, folder="ntts/branding",
                              help_text="Small square image, e.g. 64 × 64")

    # Menu button
    nav_cta_text = models.CharField("Button text", max_length=50, default="Book a Ride")
    nav_cta_opens_booking = models.BooleanField(
        "Open booking popup on click", default=True,
        help_text="Untick to send visitors to the link below instead",
    )
    nav_cta_link = models.CharField("Button link", max_length=255, blank=True, default="#book")

    # Google / SEO
    meta_title = models.CharField("Page title (Google)", max_length=70,
                                  help_text="Shown in Google results and the browser tab. Keep under 60 letters.")
    meta_description = models.CharField("Page description (Google)", max_length=170,
                                        help_text="The short text under the title in Google. Aim for 140–160 letters.")
    meta_keywords = models.CharField("Keywords", max_length=255, blank=True, help_text="Separate with commas")
    canonical_url = models.URLField("Website address", blank=True, help_text="e.g. https://www.nttsmobility.com/")
    og_title = models.CharField("Share title", max_length=100, blank=True,
                                help_text="Title when the link is shared on WhatsApp / Facebook. Leave blank to use the page title.")
    og_description = models.CharField("Share description", max_length=200, blank=True,
                                      help_text="Leave blank to use the page description.")
    og_image = CloudinaryField("Share image", blank=True, null=True, folder="ntts/seo",
                               help_text="Picture shown when the link is shared. Best size 1200 × 630.")
    robots = models.CharField("Search engine visibility", max_length=50, default="index, follow",
                              help_text='Keep "index, follow" so Google can list the site')

    class Meta:
        verbose_name = "1. Website Settings & Menu"
        verbose_name_plural = "1. Website Settings & Menu"

    def __str__(self):
        return self.site_name


class NavItem(OrderedModel):
    site = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, related_name="nav_items")
    label = models.CharField("Menu text", max_length=50)
    link = models.CharField("Goes to", max_length=255, help_text="A section like #fleet, or a full web address")
    open_in_new_tab = models.BooleanField("Open in new tab", default=False)

    class Meta(OrderedModel.Meta):
        verbose_name = "Menu link"
        verbose_name_plural = "Menu links"

    def __str__(self):
        return self.label


# ---------------------------------------------------------------------------
# 2. Hero banner
# ---------------------------------------------------------------------------
class HeroSection(SingletonModel):
    # Main heading
    badge_text = models.CharField("Small tag above heading", max_length=60, help_text="e.g. NEXT-GEN URBAN TRANSIT")
    title = models.CharField("Heading – first line", max_length=120)
    title_highlight = models.CharField("Heading – green line", max_length=120)
    description = models.TextField("Short paragraph")
    background_image = CloudinaryField("Background photo", blank=True, null=True, folder="ntts/hero",
                                       help_text="Wide landscape photo, at least 1920 px wide")
    background_alt = models.CharField("Photo description", max_length=150, blank=True,
                                      help_text="What the photo shows, for Google")

    # Phone preview
    tracking_label = models.CharField("Top tag", max_length=50, help_text="e.g. Tracking Chauffeur")
    vehicle_name = models.CharField("Car name", max_length=50)
    vehicle_details = models.CharField("Car model / colour", max_length=80)
    fleet_label = models.CharField("Right side title", max_length=50, help_text="e.g. NTTS Fleet")
    distance_text = models.CharField("Distance", max_length=30, help_text="e.g. 0.8 km away")
    driver_name = models.CharField("Driver name", max_length=50)
    driver_initials = models.CharField("Driver initials", max_length=4, help_text="Shown when there is no photo")
    driver_photo = CloudinaryField("Driver photo", blank=True, null=True, folder="ntts/hero",
                                   help_text="Optional")
    driver_rating = models.CharField("Driver rating", max_length=10, help_text="e.g. 4.98")
    driver_trips = models.CharField("Trips count", max_length=30, help_text="e.g. (1,420 trips)")
    driver_phone = models.CharField("Driver phone", max_length=20, blank=True,
                                    help_text="Optional. Makes the call icon work.")

    # Booking box
    card_title = models.CharField("Box heading", max_length=60)
    eta_text = models.CharField("Arrival time tag", max_length=40, help_text="e.g. Avg ETA 2.4 min")
    pickup_label = models.CharField("Pickup – title", max_length=40)
    pickup_placeholder = models.CharField("Pickup – example text", max_length=120,
                                          help_text="Grey hint shown inside the empty box")
    destination_label = models.CharField("Drop – title", max_length=40)
    destination_placeholder = models.CharField("Drop – example text", max_length=120,
                                               help_text="Grey hint shown inside the empty box")
    date_label = models.CharField("Date – title", max_length=30)
    date_options = models.TextField("Date – choices", help_text="Write one choice per line. The first one is picked by default.")
    ride_window_label = models.CharField("Time – title", max_length=30)
    ride_window_options = models.TextField("Time – choices", help_text="Write one choice per line. The first one is picked by default.")
    button_text = models.CharField("Button text", max_length=40)

    class Meta:
        verbose_name = "2. Hero Banner"
        verbose_name_plural = "2. Hero Banner"

    def __str__(self):
        return "Hero Banner"

    @property
    def date_option_list(self):
        return lines(self.date_options)

    @property
    def ride_window_option_list(self):
        return lines(self.ride_window_options)


# ---------------------------------------------------------------------------
# 3. Booking popup + car options
# ---------------------------------------------------------------------------
class BookingModal(SingletonModel):
    badge_text = models.CharField("Small tag", max_length=60)
    title = models.CharField("Heading", max_length=80)
    subtitle = models.CharField("Line under heading", max_length=200)

    pickup_label = models.CharField("Pickup – title", max_length=40)
    pickup_placeholder = models.CharField("Pickup – example text", max_length=120)
    destination_label = models.CharField("Drop – title", max_length=40)
    destination_placeholder = models.CharField("Drop – example text", max_length=120)

    ride_now_label = models.CharField("“Ride now” button", max_length=30)
    schedule_label = models.CharField("“Schedule” button", max_length=30)
    departing_label = models.CharField("Departure – title", max_length=30, help_text="e.g. Departing:")
    departing_highlight = models.CharField("Departure – bold text", max_length=40, help_text="e.g. Within 3–5 Mins")
    departing_note = models.CharField("Departure – note", max_length=60, help_text="e.g. (Fastest match)")
    schedule_date_label = models.CharField("Schedule – date title", max_length=30, default="Pickup Date")
    schedule_time_label = models.CharField("Schedule – time title", max_length=30, default="Pickup Time")

    vehicle_heading = models.CharField("Car list heading", max_length=60)
    nearby_suffix = models.CharField("Text after car count", max_length=40,
                                     help_text='The number is added for you: "options nearby" shows as "4 options nearby"')

    contact_heading = models.CharField("Customer details – heading", max_length=60, default="Your Details")
    name_label = models.CharField("Name – title", max_length=30, default="Full Name")
    name_placeholder = models.CharField("Name – example text", max_length=60, default="Enter your name")
    phone_label = models.CharField("Mobile – title", max_length=30, default="Mobile Number")
    phone_placeholder = models.CharField("Mobile – example text", max_length=60, default="Enter your mobile number")
    email_label = models.CharField("Email – title", max_length=30, default="Email Address")
    email_placeholder = models.CharField("Email – example text", max_length=60, default="Enter your email")

    button_prefix = models.CharField("Button – first word", max_length=30,
                                     help_text='The chosen car is added after it: "Request" shows as "Request NTTS Luxe"')
    footer_note = models.CharField("Note under button", max_length=200)

    # Thank-you popup
    success_title = models.CharField("Thank-you heading", max_length=60)
    success_message = models.CharField("Thank-you message", max_length=200)
    success_button_text = models.CharField("Close button text", max_length=30)
    success_footer_note = models.CharField("Small note at bottom", max_length=100, blank=True,
                                           help_text="Leave empty to hide it")

    class Meta:
        verbose_name = "3. Booking Popup"
        verbose_name_plural = "3. Booking Popup"

    def __str__(self):
        return "Booking Popup"


class VehicleClass(OrderedModel):
    name = models.CharField("Car type", max_length=60, help_text="e.g. Compact Sedan")
    button_name = models.CharField("Name on button", max_length=40,
                                   help_text='Shown as "Request <this>" when the car is picked')
    details = models.CharField("Short details", max_length=80, help_text="e.g. 4 seats · 3m away")
    base_price = models.DecimalField("Starting price", max_digits=8, decimal_places=2, help_text="Numbers only, e.g. 80")
    currency_symbol = models.CharField("Currency", max_length=5, default="₹")
    price_suffix = models.CharField("Text after price", max_length=20, default="base")
    badge_text = models.CharField("Highlight tag", max_length=20, blank=True,
                                  help_text='e.g. POPULAR. Leave empty for no tag.')
    is_default = models.BooleanField("Picked by default", default=False,
                                     help_text="Only one car can be picked by default")

    class Meta(OrderedModel.Meta):
        verbose_name = "Car option"
        verbose_name_plural = "3. Booking Popup – Car Options"

    def __str__(self):
        return self.name

    @property
    def price_display(self):
        value = self.base_price.normalize()
        return f"{self.currency_symbol}{value:f}"

    @property
    def photo_card(self):
        """The Fleet & Rides card whose photo this car uses (uploaded once, shown in both places)."""
        cards = [c for c in self.ride_cards.all() if c.is_active and c.image]
        return min(cards, key=lambda c: (c.order, c.pk)) if cards else None

    @property
    def photo(self):
        card = self.photo_card
        return card.image if card else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_default:
            VehicleClass.objects.exclude(pk=self.pk).filter(is_default=True).update(is_default=False)


# ---------------------------------------------------------------------------
# 4. Fleet slider
# ---------------------------------------------------------------------------
class FleetSection(SingletonModel):
    eyebrow = models.CharField("Small tag above heading", max_length=60, help_text="e.g. NTTS LIVE MOBILITY DECK")
    title = models.CharField("Heading", max_length=100)
    footer_text = models.CharField("Small text next to arrows", max_length=120, blank=True,
                                   help_text="Leave empty to hide it")
    autoplay = models.BooleanField("Change slides automatically", default=True)
    autoplay_seconds = models.PositiveIntegerField("Seconds per slide", default=6)

    class Meta:
        verbose_name = "4. Fleet Slider – Heading"
        verbose_name_plural = "4. Fleet Slider – Heading"

    def __str__(self):
        return "Fleet Slider – Heading"


class FleetSlide(OrderedModel):
    ICON_CHOICES = [
        ("sedan", "Sedan car"),
        ("city", "City car"),
        ("suv", "SUV"),
        ("ev", "Electric car"),
        ("van", "Van"),
    ]

    tab_label = models.CharField("Tab name", max_length=30, help_text="Short name on the top-right tab, e.g. Exec SUV")
    tab_icon = models.CharField("Tab icon", max_length=10, choices=ICON_CHOICES, default="sedan")
    badge_text = models.CharField("Small tag", max_length=40, blank=True, help_text="e.g. FIRST-CLASS CHAUFFEUR")
    title = models.CharField("Car name", max_length=80)
    description = models.TextField("Description")
    ride_card = models.ForeignKey(
        "RideOption", on_delete=models.SET_NULL, null=True, blank=True, related_name="fleet_slides",
        verbose_name="Use photo from Fleet & Rides card",
        help_text="The slide shows the car photo already uploaded on this card, so you don't upload it twice.",
    )
    image = CloudinaryField("Different photo (optional)", blank=True, null=True, folder="ntts/fleet",
                            help_text="Only if this slide needs its own photo. Car on a transparent background (PNG) works best.")
    image_alt = models.CharField("Photo description", max_length=150, blank=True, help_text="For Google")

    class Meta(OrderedModel.Meta):
        verbose_name = "Fleet slide"
        verbose_name_plural = "4. Fleet Slider – Slides"

    def __str__(self):
        return self.title

    @property
    def photo(self):
        """Own photo if uploaded, otherwise the linked Fleet & Rides card's photo."""
        if self.image:
            return self.image
        return self.ride_card.image if self.ride_card and self.ride_card.image else None


class FleetSpec(models.Model):
    slide = models.ForeignKey(FleetSlide, on_delete=models.CASCADE, related_name="specs")
    label = models.CharField("Title", max_length=30, help_text="e.g. Luggage")
    value = models.CharField("Value", max_length=40, help_text="e.g. 5 Suitcases")
    order = models.PositiveIntegerField("Position", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Feature"
        verbose_name_plural = "Features (shown in a row under the description)"

    def __str__(self):
        return f"{self.label}: {self.value}"


# ---------------------------------------------------------------------------
# 5. Stats (numbers row)
# ---------------------------------------------------------------------------
class StatItem(OrderedModel):
    COLOR_CHOICES = [("green", "Green"), ("dark", "Dark"), ("navy", "Navy blue")]

    number = models.CharField("Number", max_length=20, help_text="Type it as you want it shown, e.g. 10M+, 4.9, 50+, 24/7")
    show_star = models.BooleanField("Show star after number", default=False, help_text="Tick for ratings, e.g. 4.9 ★")
    label = models.CharField("Text below number", max_length=60)
    color = models.CharField("Number colour", max_length=10, choices=COLOR_CHOICES, default="green")

    class Meta(OrderedModel.Meta):
        verbose_name = "Stat box"
        verbose_name_plural = "5. Stats (numbers row)"

    def __str__(self):
        return f"{self.number} – {self.label}"


# ---------------------------------------------------------------------------
# 6. Fleet & Rides (Choose Your Ride cards)
# ---------------------------------------------------------------------------
class RidesSection(SingletonModel):
    badge_text = models.CharField("Small tag above heading", max_length=40, help_text="e.g. FLEET & RIDES")
    title = models.CharField("Heading", max_length=80)
    description = models.TextField("Short paragraph")
    side_badge_text = models.CharField("Tag on the right", max_length=60, blank=True,
                                       help_text="e.g. 100% Carbon-Neutral Fleet Options. Leave empty to hide.")

    class Meta:
        verbose_name = "6. Fleet & Rides – Heading"
        verbose_name_plural = "6. Fleet & Rides – Heading"

    def __str__(self):
        return "Fleet & Rides – Heading"


class RideOption(OrderedModel):
    name = models.CharField("Car type", max_length=60, help_text="e.g. Compact Sedan")
    currency_symbol = models.CharField("Currency", max_length=5, default="₹")
    base_price = models.DecimalField("Starting price", max_digits=8, decimal_places=2, help_text="Numbers only, e.g. 80")
    price_suffix = models.CharField("Text after price", max_length=20, default="base")
    description = models.TextField("Short description")
    image = CloudinaryField("Car photo", blank=True, null=True, folder="ntts/rides")
    image_alt = models.CharField("Photo description", max_length=150, blank=True, help_text="For Google")
    badge_text = models.CharField("Tag on photo", max_length=30, blank=True,
                                  help_text="e.g. TOP TIER. Leave empty for no tag.")
    features = models.TextField("Features", help_text="Write one feature per line, e.g. 4 Seats")
    button_text = models.CharField("Button text", max_length=30, help_text="e.g. Book Sedan")
    booking_car = models.ForeignKey(
        VehicleClass, on_delete=models.SET_NULL, null=True, blank=True, related_name="ride_cards",
        verbose_name="Linked car in booking popup",
        help_text="Clicking the button opens the booking popup with this car picked. "
                  "The photo you upload here is also shown for that car in the popup.",
    )
    is_featured = models.BooleanField("Highlight this card", default=False,
                                      help_text="Green border and filled green button")

    class Meta(OrderedModel.Meta):
        verbose_name = "Ride card"
        verbose_name_plural = "6. Fleet & Rides – Cars"

    def __str__(self):
        return self.name

    @property
    def price_display(self):
        return f"{self.currency_symbol}{self.base_price.normalize():f}"

    @property
    def feature_list(self):
        return lines(self.features)


# ---------------------------------------------------------------------------
# 7. How It Works (steps)
# ---------------------------------------------------------------------------
class StepsSection(SingletonModel):
    badge_text = models.CharField("Small tag above heading", max_length=40, help_text="e.g. THE PROCESS")
    title = models.CharField("Heading", max_length=80)
    description = models.TextField("Short paragraph")
    step_word = models.CharField("Word before step number", max_length=15, default="STEP",
                                 help_text='Numbers are added for you in order: STEP 01, STEP 02…')

    # Green banner under the steps
    show_banner = models.BooleanField("Show green banner under the steps", default=True)
    banner_title = models.CharField("Banner heading", max_length=80, blank=True)
    banner_text = models.CharField("Banner text", max_length=200, blank=True)
    banner_badge = models.CharField("Banner tag (right side)", max_length=40, blank=True,
                                    help_text="e.g. 99.98% DISPATCH UPTIME. Leave empty to hide.")

    class Meta:
        verbose_name = "7. How It Works – Heading"
        verbose_name_plural = "7. How It Works – Heading"

    def __str__(self):
        return "How It Works – Heading"


class Step(OrderedModel):
    ICON_CHOICES = [
        ("location", "Location pin"),
        ("sliders", "Settings sliders"),
        ("shield", "Safety shield"),
        ("car", "Car"),
        ("phone", "Phone"),
        ("clock", "Clock"),
        ("star", "Star"),
        ("card", "Payment card"),
    ]
    COLOR_CHOICES = [("green", "Green"), ("blue", "Blue")]

    icon = models.CharField("Icon", max_length=10, choices=ICON_CHOICES, default="location")
    color = models.CharField("Colour", max_length=10, choices=COLOR_CHOICES, default="green",
                             help_text="Colour of the step tag, icon and dot")
    title = models.CharField("Step heading", max_length=80)
    description = models.TextField("Description")
    highlight_text = models.CharField("Highlight line at bottom", max_length=80, blank=True,
                                      help_text="e.g. Instant GPS coordinate detection. Leave empty to hide.")

    class Meta(OrderedModel.Meta):
        verbose_name = "Step"
        verbose_name_plural = "7. How It Works – Steps"

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# 8. Safety
# ---------------------------------------------------------------------------
class SafetySection(SingletonModel):
    badge_text = models.CharField("Small tag above heading", max_length=60, help_text="e.g. ISO 27001 CERTIFIED SAFETY")
    title = models.CharField("Heading", max_length=80)
    description = models.TextField("Short paragraph")
    show_highlight = models.BooleanField("Show highlight box", default=True)
    highlight_title = models.CharField("Highlight box – heading", max_length=60, blank=True,
                                       help_text="e.g. NTTS Shield™ Active")
    highlight_text = models.CharField("Highlight box – text", max_length=200, blank=True)

    class Meta:
        verbose_name = "8. Safety – Heading"
        verbose_name_plural = "8. Safety – Heading"

    def __str__(self):
        return "Safety – Heading"


class SafetyFeature(OrderedModel):
    ICON_CHOICES = [
        ("id_card", "ID card"),
        ("satellite", "Satellite / GPS"),
        ("sos", "SOS / emergency"),
        ("phone_lock", "Phone with lock"),
        ("handshake", "Two-way / handshake"),
        ("shield", "Shield"),
        ("heart", "Heart / care"),
        ("camera", "Camera"),
    ]
    COLOR_CHOICES = [("green", "Green"), ("blue", "Blue"), ("red", "Red")]

    icon = models.CharField("Icon", max_length=12, choices=ICON_CHOICES, default="shield")
    color = models.CharField("Icon colour", max_length=10, choices=COLOR_CHOICES, default="green")
    title = models.CharField("Heading", max_length=60)
    description = models.TextField("Description")

    class Meta(OrderedModel.Meta):
        verbose_name = "Safety feature"
        verbose_name_plural = "8. Safety – Feature Cards"

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# 9. Pricing
# ---------------------------------------------------------------------------
class PricingSection(SingletonModel):
    badge_text = models.CharField("Small tag above heading", max_length=40, help_text="e.g. TRANSPARENT TARIFF")
    title = models.CharField("Heading", max_length=80)
    description = models.TextField("Short paragraph")

    class Meta:
        verbose_name = "9. Pricing – Heading"
        verbose_name_plural = "9. Pricing – Heading"

    def __str__(self):
        return "Pricing – Heading"


class PricingPlan(OrderedModel):
    ICON_CHOICES = [
        ("sedan", "Sedan car"),
        ("executive", "Executive car"),
        ("ev", "Electric car"),
        ("suv", "SUV / big car"),
    ]

    title = models.CharField("Plan name", max_length=40, help_text="e.g. COMPACT SEDAN")
    icon = models.CharField("Icon", max_length=10, choices=ICON_CHOICES, default="sedan")
    car = models.ForeignKey(
        VehicleClass, on_delete=models.PROTECT, related_name="pricing_plans", verbose_name="Linked car",
        help_text="The price is taken from this car in “3. Booking Popup – Car Options”, "
                  "and the button opens the booking popup with this car picked.",
    )
    price_suffix = models.CharField("Text after price", max_length=30, default="/ base fare")
    features = models.TextField("Features (with tick marks)", help_text="Write one feature per line")
    button_text = models.CharField("Button text", max_length=30, help_text="e.g. Select Sedan")
    badge_text = models.CharField("Tag on top", max_length=30, blank=True,
                                  help_text="e.g. MOST POPULAR. Leave empty for no tag.")
    is_featured = models.BooleanField("Highlight this plan", default=False,
                                      help_text="Green border and filled green button")
    COLOR_CHOICES = [("dark", "Dark"), ("green", "Green"), ("navy", "Navy blue")]
    color = models.CharField("Accent colour", max_length=10, choices=COLOR_CHOICES, default="dark",
                             help_text="Colour of the plan name and icon")

    class Meta(OrderedModel.Meta):
        verbose_name = "Pricing plan"
        verbose_name_plural = "9. Pricing – Plans"

    def __str__(self):
        return self.title

    @property
    def price_display(self):
        return self.car.price_display

    @property
    def feature_list(self):
        return lines(self.features)


# ---------------------------------------------------------------------------
# 10. Testimonials
# ---------------------------------------------------------------------------
class TestimonialsSection(SingletonModel):
    badge_text = models.CharField("Small tag above heading", max_length=40, help_text="e.g. VERIFIED RIDERS")
    title = models.CharField("Heading", max_length=80)
    description = models.TextField("Paragraph on the right")

    class Meta:
        verbose_name = "10. Testimonials – Heading"
        verbose_name_plural = "10. Testimonials – Heading"

    def __str__(self):
        return "Testimonials – Heading"


class Testimonial(OrderedModel):
    RATING_CHOICES = [(5, "★★★★★  5 stars"), (4, "★★★★  4 stars"), (3, "★★★  3 stars"),
                      (2, "★★  2 stars"), (1, "★  1 star")]

    rating = models.PositiveSmallIntegerField("Star rating", choices=RATING_CHOICES, default=5)
    quote = models.TextField("Review", help_text="Type without quotation marks; they are added for you.")
    name = models.CharField("Customer name", max_length=60)
    photo = CloudinaryField("Customer photo", blank=True, null=True, folder="ntts/testimonials",
                            help_text="Square photo works best. If empty, the initials are shown.")
    role = models.CharField("Who they are", max_length=60, help_text="e.g. Daily Tech Commuter")
    detail = models.CharField("Extra detail", max_length=40, blank=True, help_text="e.g. 340+ rides")
    is_verified = models.BooleanField("Show green verified tick", default=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "Testimonial"
        verbose_name_plural = "10. Testimonials – Reviews"

    def __str__(self):
        return self.name

    @property
    def initials(self):
        words = [w for w in self.name.replace(".", " ").split() if w[:1].isalpha()]
        return "".join(w[0] for w in words[-2:]).upper()

    @property
    def stars(self):
        return range(self.rating)


# ---------------------------------------------------------------------------
# 11. App download banner
# ---------------------------------------------------------------------------
class AppDownloadSection(SingletonModel):
    is_active = models.BooleanField("Show this section on website", default=True)
    badge_text = models.CharField("Small tag above heading", max_length=60, help_text="e.g. AVAILABLE ON IOS & ANDROID")
    title = models.CharField("Heading – first line", max_length=80)
    title_highlight = models.CharField("Heading – coloured line", max_length=80)

    text_before_code = models.CharField("Text before promo code", max_length=150)
    promo_code = models.CharField("Promo code", max_length=30, blank=True,
                                  help_text="Shown in a small box. Leave empty for no code.")
    text_after_code = models.CharField("Text after promo code", max_length=150, blank=True)

    show_app_store = models.BooleanField("Show Apple App Store button", default=True)
    app_store_small_text = models.CharField("App Store – small text", max_length=30, default="DOWNLOAD ON THE")
    app_store_text = models.CharField("App Store – big text", max_length=30, default="Apple App Store")
    app_store_link = models.URLField("App Store link", blank=True, help_text="Your app page on the Apple App Store")

    show_google_play = models.BooleanField("Show Google Play button", default=True)
    google_play_small_text = models.CharField("Google Play – small text", max_length=30, default="GET IT ON")
    google_play_text = models.CharField("Google Play – big text", max_length=30, default="Google Play")
    google_play_link = models.URLField("Google Play link", blank=True, help_text="Your app page on Google Play")

    show_qr = models.BooleanField("Show QR code box", default=True)
    qr_image = CloudinaryField("QR code image", blank=True, null=True, folder="ntts/app",
                               help_text="Upload your QR code (square PNG).")
    qr_title = models.CharField("QR box – heading", max_length=40, default="Scan to Download")
    qr_subtitle = models.CharField("QR box – small text", max_length=40, default="Instant Camera Link")

    class Meta:
        verbose_name = "11. App Download Banner"
        verbose_name_plural = "11. App Download Banner"

    def __str__(self):
        return "App Download Banner"


# ---------------------------------------------------------------------------
# 12. Footer
# ---------------------------------------------------------------------------
class FooterSettings(SingletonModel):
    about_text = models.TextField("Text under the logo")

    company_name = models.CharField("Company name", max_length=100)
    address = models.TextField("Address", help_text="Write it the way it should appear, line by line")
    map_link = models.URLField("Google Maps link", blank=True, help_text="Optional. Makes the address clickable.")
    email = models.EmailField("Email")
    helpdesk_label = models.CharField("Mobile – title", max_length=30, default="Help Desk")
    helpdesk_phone = models.CharField("Mobile number", max_length=20)
    landline_label = models.CharField("Landline – title", max_length=30, default="Land Line")
    landline_phone = models.CharField("Landline number", max_length=20, blank=True)

    copyright_text = models.CharField(
        "Copyright line", max_length=150,
        help_text="Tip: type {year} to always show the current year, e.g. © {year} NTTS Mobility Technologies.",
    )

    # Developer credit (bottom-right of the footer)
    credit_text = models.CharField("Credit text", max_length=100, blank=True,
                                   default="Designed & Developed by Vetri IT Systems",
                                   help_text="Leave empty to hide it")
    credit_link = models.URLField("Credit link", blank=True, default="https://vetriitsystems.com/",
                                  help_text="Opens in a new tab when the credit text is clicked")

    # Floating WhatsApp / Email / Call buttons (bottom-right of every page)
    show_floating_buttons = models.BooleanField("Show floating contact buttons", default=True)
    whatsapp_number = models.CharField("WhatsApp number", max_length=20, blank=True,
                                       help_text="10-digit mobile number. Leave empty to hide the WhatsApp button.")
    whatsapp_message = models.CharField("WhatsApp starting message", max_length=200, blank=True,
                                        help_text="Typed for the customer when WhatsApp opens (they can change it)")
    show_email_button = models.BooleanField("Show email button", default=True, help_text="Uses the Email above")
    show_call_button = models.BooleanField("Show call button", default=True, help_text="Uses the Mobile number above")

    class Meta:
        verbose_name = "12. Footer – Main"
        verbose_name_plural = "12. Footer – Main"

    def __str__(self):
        return "Footer"

    @property
    def address_lines(self):
        return lines(self.address)

    @property
    def copyright_display(self):
        return self.copyright_text.replace("{year}", str(timezone.localdate().year))

    @staticmethod
    def tel(number):
        return "".join(ch for ch in number if ch.isdigit() or ch == "+")

    @property
    def whatsapp_link(self):
        from urllib.parse import quote
        digits = "".join(ch for ch in self.whatsapp_number if ch.isdigit())
        if len(digits) == 10:
            digits = "91" + digits
        if not digits:
            return ""
        return f"https://wa.me/{digits}" + (f"?text={quote(self.whatsapp_message)}" if self.whatsapp_message else "")

    @property
    def helpdesk_tel(self):
        return self.tel(self.helpdesk_phone)

    @property
    def landline_tel(self):
        return self.tel(self.landline_phone)


class SocialLink(OrderedModel):
    PLATFORM_CHOICES = [
        ("website", "Website (globe)"),
        ("share", "Share"),
        ("heart", "Heart"),
        ("facebook", "Facebook"),
        ("instagram", "Instagram"),
        ("x", "X (Twitter)"),
        ("linkedin", "LinkedIn"),
        ("youtube", "YouTube"),
        ("whatsapp", "WhatsApp"),
    ]

    footer = models.ForeignKey(FooterSettings, on_delete=models.CASCADE, related_name="social_links")
    platform = models.CharField("Icon", max_length=12, choices=PLATFORM_CHOICES)
    link = models.CharField("Link", max_length=255, help_text="Full web address, e.g. https://instagram.com/…")

    class Meta(OrderedModel.Meta):
        verbose_name = "Social icon"
        verbose_name_plural = "Social icons (under the text)"

    def __str__(self):
        return self.get_platform_display()


class FooterColumn(OrderedModel):
    title = models.CharField("Column heading", max_length=40, help_text="e.g. COMPANY")

    class Meta(OrderedModel.Meta):
        verbose_name = "Footer link column"
        verbose_name_plural = "12. Footer – Link Columns"

    def __str__(self):
        return self.title


class FooterLink(OrderedModel):
    column = models.ForeignKey(FooterColumn, on_delete=models.CASCADE, related_name="links")
    label = models.CharField("Link text", max_length=50)
    link = models.CharField("Goes to", max_length=255, default="#",
                            help_text="A section like #safety, a page, or a full web address")
    open_in_new_tab = models.BooleanField("Open in new tab", default=False)

    class Meta(OrderedModel.Meta):
        verbose_name = "Link"
        verbose_name_plural = "Links in this column"

    def __str__(self):
        return self.label


# ---------------------------------------------------------------------------
# Ride bookings received from the website
# ---------------------------------------------------------------------------
class BookingRequest(models.Model):
    RIDE_NOW = "now"
    SCHEDULE = "schedule"
    RIDE_TYPES = [(RIDE_NOW, "Ride Now"), (SCHEDULE, "Scheduled")]

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("confirmed", "Confirmed"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    pickup = models.CharField("Pickup", max_length=255)
    destination = models.CharField("Drop", max_length=255)
    ride_type = models.CharField("Ride type", max_length=10, choices=RIDE_TYPES, default=RIDE_NOW)
    scheduled_date = models.DateField("Pickup date", null=True, blank=True)
    scheduled_time = models.TimeField("Pickup time", null=True, blank=True)
    date_option = models.CharField("Date chosen", max_length=60, blank=True)
    ride_window = models.CharField("Time chosen", max_length=60, blank=True)

    vehicle = models.ForeignKey(VehicleClass, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Car option")
    vehicle_name = models.CharField("Car", max_length=60, blank=True)
    quoted_price = models.CharField("Price shown", max_length=20, blank=True)

    name = models.CharField("Name", max_length=100)
    phone = models.CharField("Mobile", max_length=20)
    email = models.EmailField("Email", blank=True)

    status = models.CharField("Status", max_length=12, choices=STATUS_CHOICES, default="new")
    admin_notes = models.TextField("Your notes", blank=True, help_text="Only visible to you")
    ip_address = models.GenericIPAddressField("IP address", null=True, blank=True)
    email_sent = models.BooleanField("Email alert sent", default=False)
    created_at = models.DateTimeField("Received on", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Ride booking"
        verbose_name_plural = "Ride Bookings (from website)"

    def __str__(self):
        return f"{self.name} · {self.pickup} → {self.destination}"
