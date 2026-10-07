from cloudinary.models import CloudinaryField
from django.core.exceptions import ValidationError
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
    tab_labels = models.TextField("Trip tabs", blank=True,
                                  help_text="Write one tab name per line, e.g. Airport Cab. Leave empty to hide the tabs.")
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
    pricing_button_text = models.CharField("Second button text", max_length=40, default="Pricing Details",
                                           help_text="Scrolls down to the Pricing section.")

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

    @property
    def tab_label_list(self):
        return lines(self.tab_labels)


# ---------------------------------------------------------------------------
# 3. Booking popup + car options
# ---------------------------------------------------------------------------
class BookingModal(SingletonModel):
    badge_text = models.CharField("Small tag", max_length=60)
    title = models.CharField("Heading", max_length=80)
    subtitle = models.CharField("Line under heading", max_length=200)

    airport_tab_label = models.CharField("Tab 1 – Airport", max_length=40, default="Airport Transfer")
    local_tab_label = models.CharField("Tab 2 – Local", max_length=40, default="Local – Hourly Rentals")
    outstation_tab_label = models.CharField("Tab 3 – Outstation", max_length=40, default="Outstation")

    pickup_label = models.CharField("Pickup – title", max_length=40)
    pickup_placeholder = models.CharField("Pickup – example text", max_length=120)
    destination_label = models.CharField("Drop – title", max_length=40, help_text="Shown on the Airport tab")
    destination_placeholder = models.CharField("Drop – example text", max_length=120)
    location_suggestions = models.TextField(
        "Pickup / Drop suggestions", blank=True,
        help_text="Place names shown as the customer types, one per line, e.g. T. Nagar. Leave empty to turn off.")

    schedule_date_label = models.CharField("Date – title", max_length=30, default="Pickup Date")
    schedule_time_label = models.CharField("Time – title", max_length=30, default="Pickup Time")
    flight_label = models.CharField("Flight number – title", max_length=30, default="Flight Number",
                                    help_text="Airport tab")
    flight_placeholder = models.CharField("Flight number – example text", max_length=60, default="e.g. 6E 2134")
    days_label = models.CharField("Days – title", max_length=30, default="No of Days", help_text="Outstation tab")
    pax_label = models.CharField("Passengers – title", max_length=30, default="No of Pax", help_text="Outstation tab")
    package_heading = models.CharField("Package list heading", max_length=60, default="Select the Package",
                                       help_text="Local – Hourly Rentals tab")
    local_terms = models.TextField("Local – terms & conditions", blank=True,
                                   help_text="Shown under the packages on the Local – Hourly Rentals tab. "
                                             "One point per line. Leave empty to hide it.")

    vehicle_heading = models.CharField("Car list heading", max_length=60)
    nearby_suffix = models.CharField("Text after car count", max_length=40,
                                     help_text='The number is added for you: "options" shows as "4 options"')
    no_cars_text = models.CharField("Text when no car has a price", max_length=150,
                                    default="No cars are available for this trip yet. Please call us to book.")

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

    @property
    def location_list(self):
        return lines(self.location_suggestions)


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
    seats = models.PositiveSmallIntegerField("Passenger seats", default=4,
                                             help_text="On the Outstation tab, cars with fewer seats than "
                                                       "“No of Pax” can't be picked")

    class Meta(OrderedModel.Meta):
        verbose_name = "Car option"
        verbose_name_plural = "3. Booking Popup – Car Options"

    def __str__(self):
        return self.name

    @property
    def price_display(self):
        return money(self.base_price, self.currency_symbol)  # ₹1,400

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


# The 3 tabs in the booking popup
AIRPORT = "airport"
LOCAL = "local"
OUTSTATION = "outstation"
TRIP_TYPES = [(AIRPORT, "Airport Transfer"), (LOCAL, "Local – Hourly Rental"), (OUTSTATION, "Outstation")]


def money(value, symbol="₹"):
    """₹1,200 or ₹14.50 (no trailing .00)."""
    if value is None:
        return ""
    text = f"{value:,.0f}" if value == value.to_integral() else f"{value:,.2f}"
    return f"{symbol}{text}"


class RentalPackage(OrderedModel):
    name = models.CharField("Package", max_length=40, help_text="e.g. 4 Hrs / 40 Km")

    class Meta(OrderedModel.Meta):
        verbose_name = "Local package"
        verbose_name_plural = "3. Booking Popup – Local Packages"

    def __str__(self):
        return self.name


class TripRate(models.Model):
    vehicle = models.ForeignKey(VehicleClass, on_delete=models.CASCADE, related_name="trip_rates",
                                verbose_name="Car")
    trip_type = models.CharField("Trip", max_length=12, choices=TRIP_TYPES)
    package = models.ForeignKey(RentalPackage, on_delete=models.CASCADE, null=True, blank=True,
                                related_name="rates", verbose_name="Package",
                                help_text="Only for Local – Hourly Rental")
    price = models.DecimalField("Price", max_digits=9, decimal_places=2, help_text="Numbers only, e.g. 1200")
    price_suffix = models.CharField("Text after price", max_length=30, blank=True,
                                    help_text="e.g. fixed, per day (250 Km). Can be empty.")
    extra_km_rate = models.DecimalField("Extra per Km", max_digits=7, decimal_places=2, null=True, blank=True)
    extra_hour_rate = models.DecimalField("Extra per hour", max_digits=7, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField("Show on website", default=True)

    class Meta:
        ordering = ["vehicle__order", "vehicle_id", "trip_type", "package__order", "id"]
        verbose_name = "Price"
        verbose_name_plural = "3. Booking Popup – Prices"

    def __str__(self):
        return f"{self.vehicle} · {self.trip_label}"

    def clean(self):
        if self.trip_type == LOCAL and not self.package_id:
            raise ValidationError({"package": "Please choose a package for Local – Hourly Rental."})
        if self.trip_type != LOCAL and self.package_id:
            raise ValidationError({"package": "Packages are only for Local – Hourly Rental. Please leave it empty."})
        if self.vehicle_id and self.trip_type:
            same = TripRate.objects.filter(vehicle_id=self.vehicle_id, trip_type=self.trip_type,
                                           package_id=self.package_id).exclude(pk=self.pk)
            if same.exists():
                raise ValidationError("This car already has a price for this trip"
                                      + (" and package." if self.package_id else "."))

    @property
    def trip_label(self):
        label = self.get_trip_type_display()
        return f"{label} – {self.package}" if self.package_id else label

    @property
    def price_display(self):
        return money(self.price, self.vehicle.currency_symbol)

    @property
    def quote(self):
        return f"{self.price_display} {self.price_suffix}".strip()

    @property
    def extras(self):
        """e.g. "₹14/Km · ₹150/hour" (empty when there are no extra rates)."""
        symbol = self.vehicle.currency_symbol
        parts = []
        if self.extra_km_rate:
            parts.append(f"{money(self.extra_km_rate, symbol)}/Km")
        if self.extra_hour_rate:
            parts.append(f"{money(self.extra_hour_rate, symbol)}/hour")
        return " · ".join(parts)


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
    description = models.TextField("Description",
                                   help_text="To make words bold, put two stars on each side: **AC sedan cabs**")
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
    link = models.URLField("Link", blank=True,
                           help_text="Optional. Clicking the box opens this page in a new tab, e.g. Google reviews.")

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
    description = models.TextField("Short paragraph",
                                   help_text="To make words bold, put two stars on each side: **cab booking**")
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
    subtitle = models.CharField("Line under car type", max_length=80, blank=True,
                                help_text="e.g. Affordable City & Daily Travel. Leave empty to hide it.")
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
        return money(self.base_price, self.currency_symbol)  # ₹1,400

    @property
    def feature_list(self):
        return lines(self.features)


# ---------------------------------------------------------------------------
# 7. How It Works (steps)
# ---------------------------------------------------------------------------
class StepsSection(SingletonModel):
    badge_text = models.CharField("Small tag above heading", max_length=40, help_text="e.g. THE PROCESS")
    title = models.CharField("Heading", max_length=80)
    description = models.TextField("Short paragraph",
                                   help_text="To make words bold, put two stars on each side: **cab or taxi online**")
    step_word = models.CharField("Word before step number", max_length=15, default="STEP",
                                 help_text='Numbers are added for you in order: STEP 01, STEP 02…')

    # Green banner under the steps
    show_banner = models.BooleanField("Show green banner under the steps", default=True)
    banner_title = models.CharField("Banner heading", max_length=80, blank=True)
    banner_text = models.CharField("Banner text", max_length=300, blank=True,
                                   help_text="To make words bold, put two stars on each side: **cab for city travel**")
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
    description = models.TextField("Description",
                                   help_text="To make words bold, put two stars on each side: **cab fare**")
    highlight_text = models.CharField("Highlight line at bottom", max_length=200, blank=True,
                                      help_text="e.g. **Live Ride Tracking –** Stay updated on your driver. "
                                                "Words between ** show in bold green. Leave empty to hide.")

    class Meta(OrderedModel.Meta):
        verbose_name = "Step"
        verbose_name_plural = "7. How It Works – Steps"

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# 8. Safety
# ---------------------------------------------------------------------------
class SafetySection(SingletonModel):
    badge_text = models.CharField("Small tag above heading", max_length=60, blank=True,
                                  help_text="e.g. ISO 27001 CERTIFIED SAFETY. Leave empty to hide it.")
    title = models.CharField("Heading", max_length=80)
    description = models.TextField("Short paragraph",
                                   help_text="To make words bold, put two stars on each side: **online cab booking**")
    show_highlight = models.BooleanField("Show highlight box", default=True)
    highlight_title = models.CharField("Highlight box – heading", max_length=60, blank=True,
                                       help_text="e.g. NTTS Shield™ Active")
    highlight_text = models.CharField("Highlight box – text", max_length=400, blank=True,
                                      help_text="To make words bold, put two stars on each side: **taxi booking**")
    highlight_tag = models.CharField("Highlight box – green line at bottom", max_length=60, blank=True,
                                     help_text="e.g. 24/7 Ride Monitoring. Leave empty to hide it.")

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
    subtitle = models.CharField("Line under heading", max_length=80, blank=True,
                                help_text="e.g. Trusted Drivers for Every Journey. Leave empty to hide it.")
    description = models.TextField("Description")
    check_text = models.CharField("Green tick line at bottom", max_length=80, blank=True,
                                  help_text="e.g. Verified Driver Screening (the ✓ is added for you). Leave empty to hide it.")

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
    description = models.TextField("Short paragraph",
                                   help_text="To make words bold, put two stars on each side: **cab booking**")
    highlights = models.TextField("Green points under the paragraph", blank=True,
                                  help_text="Write one point per line, e.g. No Hidden Charges. Leave empty to hide them.")

    class Meta:
        verbose_name = "9. Pricing – Heading"
        verbose_name_plural = "9. Pricing – Heading"

    def __str__(self):
        return "Pricing – Heading"

    @property
    def highlight_list(self):
        return lines(self.highlights)


class PricingPlan(OrderedModel):
    ICON_CHOICES = [
        ("sedan", "Sedan car"),
        ("executive", "Executive car"),
        ("ev", "Electric car"),
        ("suv", "SUV / big car"),
    ]

    title = models.CharField("Plan name", max_length=40, help_text="e.g. COMPACT SEDAN")
    subtitle = models.CharField("Line under plan name", max_length=60, blank=True,
                                help_text="e.g. Affordable Sedan Cab. Leave empty to hide it.")
    description = models.CharField("Short description", max_length=250, blank=True,
                                   help_text="Shown under the price. Leave empty to hide it.")
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
    description = models.TextField("Paragraph on the right",
                                   help_text="To make words bold, put two stars on each side: **reliable cab booking**")

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
    role = models.CharField("Who they are", max_length=60, blank=True,
                            help_text="e.g. Daily Tech Commuter. Leave empty to hide.")
    detail = models.CharField("Extra detail", max_length=40, blank=True, help_text="e.g. 340+ rides")
    is_verified = models.BooleanField("Show green verified tick", default=True)

    class Meta(OrderedModel.Meta):
        verbose_name = "Testimonial"
        verbose_name_plural = "10. Testimonials – Reviews"

    def __str__(self):
        return self.name

    @property
    def initials(self):
        """First letter of the name, shown when there is no photo."""
        letters = [ch for ch in self.name if ch.isalpha()]
        return letters[0].upper() if letters else "?"

    @property
    def stars(self):
        return range(self.rating)


# ---------------------------------------------------------------------------
# 11. FAQ
# ---------------------------------------------------------------------------
class FAQSection(SingletonModel):
    is_active = models.BooleanField("Show this section on website", default=True)
    badge_text = models.CharField("Small tag above heading", max_length=40, blank=True, help_text="e.g. FAQ")
    title = models.CharField("Heading", max_length=100)
    description = models.TextField("Short paragraph", blank=True)

    # Help box under the paragraph (left side)
    show_help_box = models.BooleanField("Show “still have questions” box", default=True)
    help_title = models.CharField("Help box – heading", max_length=60, blank=True)
    help_text = models.CharField("Help box – text", max_length=200, blank=True)
    help_button_text = models.CharField("Help box – call button text", max_length=40, blank=True,
                                        help_text="Calls the Help Desk number from “12. Footer – Main”. Leave empty to hide.")

    class Meta:
        verbose_name = "11. FAQ – Heading"
        verbose_name_plural = "11. FAQ – Heading"

    def __str__(self):
        return "FAQ – Heading"


class FAQItem(OrderedModel):
    question = models.CharField("Question", max_length=200)
    answer = models.TextField("Answer", help_text="Write each paragraph on its own line")

    class Meta(OrderedModel.Meta):
        verbose_name = "Question"
        verbose_name_plural = "11. FAQ – Questions"

    def __str__(self):
        return self.question

    @property
    def answer_paragraphs(self):
        return lines(self.answer)


# ---------------------------------------------------------------------------
# 13. About Us
# ---------------------------------------------------------------------------
class AboutSection(SingletonModel):
    is_active = models.BooleanField("Show this section on website", default=True)
    badge_text = models.CharField("Small tag above heading", max_length=40, blank=True, help_text="e.g. ABOUT US")
    title = models.CharField("Heading", max_length=100)
    description = models.TextField("Paragraphs", help_text="Write each paragraph on its own line")
    image = CloudinaryField("Photo", blank=True, null=True, folder="ntts/about",
                            help_text="Optional. Office, team or fleet photo (landscape works best).")
    image_alt = models.CharField("Photo description", max_length=150, blank=True, help_text="For Google")

    services_heading = models.CharField("Services – heading", max_length=60, blank=True,
                                        help_text="e.g. Our Fleet Services. Leave empty to hide the list.")
    services = models.TextField("Services", blank=True, help_text="Write one service per line")

    mission_title = models.CharField("Card 1 – heading", max_length=60, blank=True, help_text="e.g. Mission. Leave empty to hide.")
    mission_text = models.CharField("Card 1 – text", max_length=300, blank=True)
    vision_title = models.CharField("Card 2 – heading", max_length=60, blank=True, help_text="e.g. Vision. Leave empty to hide.")
    vision_text = models.CharField("Card 2 – text", max_length=300, blank=True)
    why_title = models.CharField("Card 3 – heading", max_length=60, blank=True, help_text="e.g. Why NTTS. Leave empty to hide.")
    why_text = models.CharField("Card 3 – text", max_length=300, blank=True)

    values_heading = models.CharField("Values row – heading", max_length=60, blank=True,
                                      help_text="e.g. Our Value Add. The value cards are added at the bottom of this page.")

    class Meta:
        verbose_name = "13. About Us"
        verbose_name_plural = "13. About Us"

    def __str__(self):
        return "About Us"

    @property
    def paragraphs(self):
        return lines(self.description)

    @property
    def active_values(self):
        return [v for v in self.values.all() if v.is_active]

    @property
    def service_list(self):
        return lines(self.services)

    @property
    def cards(self):
        """Mission / Vision / Why cards that have a heading, as (key, heading, text)."""
        return [(key, title, text) for key, title, text in (
            ("mission", self.mission_title, self.mission_text),
            ("vision", self.vision_title, self.vision_text),
            ("why", self.why_title, self.why_text),
        ) if title]


class AboutValue(OrderedModel):
    ICON_CHOICES = [
        ("award", "Award / badge"),
        ("clock", "Clock"),
        ("target", "Target"),
        ("shield", "Shield"),
        ("star", "Star"),
        ("handshake", "Handshake"),
    ]

    section = models.ForeignKey(AboutSection, on_delete=models.CASCADE, related_name="values")
    icon = models.CharField("Icon", max_length=12, choices=ICON_CHOICES, default="award")
    title = models.CharField("Heading", max_length=60)
    text = models.CharField("Text", max_length=250)

    class Meta(OrderedModel.Meta):
        verbose_name = "Value card"
        verbose_name_plural = "Value cards (e.g. Professionalism, Punctuality, Precision)"

    def __str__(self):
        return self.title


# ---------------------------------------------------------------------------
# 12. Footer
# ---------------------------------------------------------------------------
class FooterSettings(SingletonModel):
    tagline = models.CharField("Heading under the logo", max_length=80, blank=True,
                               help_text="e.g. Safe & Reliable Mobility for the Modern City. Leave empty to hide it.")
    about_text = models.TextField("Text under the logo",
                                  help_text="To make words bold, put two stars on each side: **online cab booking**")
    highlights = models.TextField("Green points under the text", blank=True,
                                  help_text="Write one point per line, e.g. Safe Rides. Leave empty to hide them.")

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
    def highlight_list(self):
        return lines(self.highlights)

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

    trip_type = models.CharField("Trip", max_length=12, choices=TRIP_TYPES, blank=True)
    pickup = models.CharField("Pickup", max_length=255)
    destination = models.CharField("Drop", max_length=255, blank=True)
    ride_type = models.CharField("Ride type", max_length=10, choices=RIDE_TYPES, default=RIDE_NOW)
    scheduled_date = models.DateField("Pickup date", null=True, blank=True)
    scheduled_time = models.TimeField("Pickup time", null=True, blank=True)
    date_option = models.CharField("Date chosen", max_length=60, blank=True)
    ride_window = models.CharField("Time chosen", max_length=60, blank=True)
    flight_number = models.CharField("Flight number", max_length=12, blank=True)
    package_name = models.CharField("Package", max_length=40, blank=True)
    num_days = models.PositiveSmallIntegerField("No of days", null=True, blank=True)
    num_pax = models.PositiveSmallIntegerField("No of pax", null=True, blank=True)

    vehicle = models.ForeignKey(VehicleClass, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Car option")
    vehicle_name = models.CharField("Car", max_length=60, blank=True)
    quoted_price = models.CharField("Price shown", max_length=60, blank=True)
    extra_charges = models.CharField("Extra charges shown", max_length=80, blank=True)

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
        route = f"{self.pickup} → {self.destination}" if self.destination else self.pickup
        return f"{self.name} · {route}"

    @property
    def reference(self):
        return f"NT-{self.pk:05d}" if self.pk else ""

    @property
    def trip_label(self):
        return self.get_trip_type_display() or "Ride"

    @property
    def when_text(self):
        if self.scheduled_date:
            text = f"{self.scheduled_date:%a, %d %b %Y}"
            return f"{text}, {self.scheduled_time:%I:%M %p}" if self.scheduled_time else text
        return self.ride_window or self.date_option or "Now"

    @property
    def trip_rows(self):
        """[(label, value), …] of the trip details the customer filled in (used in emails)."""
        rows = [("Trip", self.trip_label), ("Pickup at", self.pickup)]
        if self.destination:
            rows.append(("Drop at", self.destination))
        if self.scheduled_date:
            rows.append(("Pickup date", f"{self.scheduled_date:%a, %d %b %Y}"))
        if self.scheduled_time:
            rows.append(("Pickup time", f"{self.scheduled_time:%I:%M %p}"))
        if not self.scheduled_date:
            rows.append(("When", self.when_text))
        if self.flight_number:
            rows.append(("Flight number", self.flight_number))
        if self.package_name:
            rows.append(("Package", self.package_name))
        if self.num_days:
            rows.append(("No of days", str(self.num_days)))
        if self.num_pax:
            rows.append(("No of pax", str(self.num_pax)))
        return rows

    @property
    def customer_rows(self):
        rows = [("Name", self.name), ("Mobile", self.phone)]
        if self.email:
            rows.append(("Email", self.email))
        return rows

    @property
    def fare_rows(self):
        rows = [("Car", self.vehicle_name), ("Fare", self.quoted_price)]
        if self.extra_charges:
            rows.append(("Extra charges", self.extra_charges))
        return rows


# ---------------------------------------------------------------------------
# 14. Policy popups (Privacy Policy, Terms) opened from footer links
# ---------------------------------------------------------------------------
class LegalPage(OrderedModel):
    title = models.CharField("Title", max_length=80, help_text="e.g. Privacy Policy")
    slug = models.SlugField(
        "Link name", max_length=60, unique=True,
        help_text="To open this popup from a footer link, set that link's “Goes to” to # + this name, "
                  "e.g. #privacy-policy",
    )
    intro = models.TextField("Opening line", blank=True)
    content = models.TextField(
        "Content",
        help_text="Write one point per line. Start a line with # to make it a heading, e.g. # Cancellations",
    )
    updated_on = models.DateField("Last updated", default=timezone.localdate)

    class Meta(OrderedModel.Meta):
        verbose_name = "Policy popup"
        verbose_name_plural = "14. Policy Popups (Privacy, Terms)"

    def __str__(self):
        return self.title

    @property
    def sections(self):
        """[(heading, [points]), …] from the content lines."""
        sections = []
        for line in lines(self.content):
            if line.startswith("#"):
                sections.append((line.lstrip("#").strip(), []))
            else:
                if not sections:
                    sections.append(("", []))
                sections[-1][1].append(line)
        return sections
