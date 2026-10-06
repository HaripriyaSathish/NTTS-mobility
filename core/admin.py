from django import forms
from django.contrib import admin
from django.db import models
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    AboutSection,
    AboutValue,
    FooterColumn,
    FooterLink,
    FooterSettings,
    SocialLink,
    BookingModal,
    BookingRequest,
    FAQItem,
    FAQSection,
    FleetSection,
    FleetSlide,
    FleetSpec,
    HeroSection,
    LegalPage,
    NavItem,
    PricingPlan,
    PricingSection,
    RentalPackage,
    RideOption,
    RidesSection,
    SafetyFeature,
    SafetySection,
    SiteSettings,
    SMTPSettings,
    StatItem,
    Step,
    StepsSection,
    Testimonial,
    TestimonialsSection,
    TripRate,
    VehicleClass,
)

admin.site.site_header = "NTTS Mobility – Website Admin"
admin.site.site_title = "NTTS Mobility Admin"
admin.site.index_title = "Edit your website"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SMALL_TEXTAREA = {models.TextField: {"widget": forms.Textarea(attrs={"rows": 3, "cols": 80})}}


def image_preview(field, height=60):
    if not field:
        return "No image uploaded yet"
    return format_html('<img src="{}" style="height:{}px;border-radius:6px">', field.url, height)


class SingletonAdmin(admin.ModelAdmin):
    """One record only: clicking the section opens its edit page directly."""

    formfield_overrides = SMALL_TEXTAREA

    def has_add_permission(self, request):
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        opts = self.model._meta
        obj = self.model.objects.first()
        if obj:
            return redirect(reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk]))
        return redirect(reverse(f"admin:{opts.app_label}_{opts.model_name}_add"))

    def response_change(self, request, obj):
        # After saving, stay on the same page instead of an one-item list
        if "_continue" not in request.POST and "_addanother" not in request.POST:
            self.message_user(request, "Saved. Your changes are live on the website.")
            return redirect(request.path)
        return super().response_change(request, obj)


def show_on_site(modeladmin, request, queryset):
    queryset.update(is_active=True)


def hide_from_site(modeladmin, request, queryset):
    queryset.update(is_active=False)


show_on_site.short_description = "Show selected on website"
hide_from_site.short_description = "Hide selected from website"


# ---------------------------------------------------------------------------
# Email settings (SMTP)
# ---------------------------------------------------------------------------
class SMTPSettingsForm(forms.ModelForm):
    password = forms.CharField(
        label="App password",
        widget=forms.PasswordInput(render_value=False),
        required=False,
        help_text="Leave empty to keep the saved password.",
    )

    class Meta:
        model = SMTPSettings
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("use_tls") and cleaned.get("use_ssl"):
            raise forms.ValidationError("Tick either TLS or SSL, not both.")
        if not cleaned.get("password"):
            if self.instance.pk and self.instance.password:
                cleaned["password"] = self.instance.password
            else:
                self.add_error("password", "Please enter the app password.")
        return cleaned


@admin.register(SMTPSettings)
class SMTPSettingsAdmin(SingletonAdmin):
    form = SMTPSettingsForm
    fieldsets = (
        ("Where to send booking alerts", {"fields": ("receiver_email", "is_active")}),
        ("Sending account", {
            "description": "The email account the website uses to send mails.",
            "fields": ("from_email", "username", "password"),
        }),
        ("Server (usually no need to change)", {"fields": ("host", "port", "use_tls", "use_ssl")}),
    )


# ---------------------------------------------------------------------------
# 1. Website settings & menu
# ---------------------------------------------------------------------------
class NavItemInline(admin.TabularInline):
    model = NavItem
    extra = 0
    fields = ("label", "link", "order", "is_active", "open_in_new_tab")
    verbose_name_plural = "Menu links (top bar)"


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonAdmin):
    inlines = [NavItemInline]
    readonly_fields = ("logo_preview", "og_image_preview")
    fieldsets = (
        ("Logo & name", {"fields": ("site_name", "logo", "logo_preview", "logo_alt", "favicon")}),
        ("Menu button (top right)", {"fields": ("nav_cta_text", "nav_cta_opens_booking", "nav_cta_link")}),
        ("Google search", {
            "description": "How your website appears in Google results.",
            "fields": ("meta_title", "meta_description", "meta_keywords", "canonical_url"),
        }),
        ("Sharing on WhatsApp / Facebook", {"fields": ("og_title", "og_description", "og_image", "og_image_preview")}),
        ("Advanced", {"classes": ("collapse",), "fields": ("robots",)}),
    )

    @admin.display(description="Current logo")
    def logo_preview(self, obj):
        return image_preview(obj.logo)

    @admin.display(description="Current share image")
    def og_image_preview(self, obj):
        return image_preview(obj.og_image, 100)


# ---------------------------------------------------------------------------
# 2. Hero banner
# ---------------------------------------------------------------------------
@admin.register(HeroSection)
class HeroSectionAdmin(SingletonAdmin):
    readonly_fields = ("background_preview", "driver_photo_preview")
    fieldsets = (
        ("Main heading", {
            "description": "The big text on the right side of the banner.",
            "fields": ("badge_text", "title", "title_highlight", "description"),
        }),
        ("Background photo", {"fields": ("background_image", "background_preview", "background_alt")}),
        ("Phone preview (left side)", {
            "description": "The live-tracking card shown inside the phone.",
            "fields": (
                "tracking_label",
                ("vehicle_name", "vehicle_details"),
                ("fleet_label", "distance_text"),
                ("driver_name", "driver_initials"),
                ("driver_rating", "driver_trips"),
                "driver_photo", "driver_photo_preview",
                "driver_phone",
            ),
        }),
        ("Booking box", {
            "description": "The white booking box under the heading.",
            "fields": (
                ("card_title", "eta_text"),
                "tab_labels",
                ("pickup_label", "pickup_placeholder"),
                ("destination_label", "destination_placeholder"),
                ("date_label", "date_options"),
                ("ride_window_label", "ride_window_options"),
                "button_text",
            ),
        }),
    )

    @admin.display(description="Current photo")
    def background_preview(self, obj):
        return image_preview(obj.background_image, 120)

    @admin.display(description="Current driver photo")
    def driver_photo_preview(self, obj):
        return image_preview(obj.driver_photo, 60)


# ---------------------------------------------------------------------------
# 3. Booking popup & car options
# ---------------------------------------------------------------------------
@admin.register(BookingModal)
class BookingModalAdmin(SingletonAdmin):
    fieldsets = (
        ("Top of popup", {"fields": ("badge_text", "title", "subtitle")}),
        ("Trip tabs", {"fields": (("airport_tab_label", "local_tab_label", "outstation_tab_label"),)}),
        ("Trip boxes", {"fields": (("pickup_label", "pickup_placeholder"),
                                  ("destination_label", "destination_placeholder"),
                                  ("schedule_date_label", "schedule_time_label"),
                                  ("flight_label", "flight_placeholder"),
                                  ("days_label", "pax_label"),
                                  "package_heading", "local_terms")}),
        ("Car list", {
            "description": "Prices are edited in “3. Booking Popup – Prices” (or inside each car). "
                           "Local packages are edited in “3. Booking Popup – Local Packages”.",
            "fields": ("vehicle_heading", "nearby_suffix", "no_cars_text"),
        }),
        ("Customer details", {"fields": ("contact_heading",
                                         ("name_label", "name_placeholder"),
                                         ("phone_label", "phone_placeholder"),
                                         ("email_label", "email_placeholder"))}),
        ("Send button", {"fields": ("button_prefix", "footer_note")}),
        ("Thank-you popup (after booking)", {"fields": ("success_title", "success_message",
                                                       "success_button_text", "success_footer_note")}),
    )


class TripRateInline(admin.TabularInline):
    model = TripRate
    extra = 0
    fields = ("trip_type", "package", "price", "price_suffix", "extra_km_rate", "extra_hour_rate", "is_active")
    verbose_name = "Price"
    verbose_name_plural = "Prices in the booking popup (Airport / Local packages / Outstation)"


@admin.register(VehicleClass)
class VehicleClassAdmin(admin.ModelAdmin):
    inlines = [TripRateInline]
    list_display = ("thumb", "name", "details", "seats", "price", "badge_text", "is_default", "order", "is_active")
    list_display_links = ("thumb", "name")
    list_editable = ("order", "is_active")
    actions = [show_on_site, hide_from_site]
    readonly_fields = ("photo_info",)
    fieldsets = (
        ("Car", {"fields": ("name", "details", "seats", "badge_text")}),
        ("Photo", {"fields": ("photo_info",)}),
        ("Starting price", {
            "description": "Shown on the Fleet & Rides and Pricing cards. "
                           "The booking popup uses the prices in the table below.",
            "fields": (("currency_symbol", "base_price", "price_suffix"),),
        }),
        ("Booking button", {"fields": ("button_name", "is_default")}),
        ("Display", {"fields": ("order", "is_active")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("ride_cards")

    @admin.display(description="Photo")
    def thumb(self, obj):
        return image_preview(obj.photo, 36)

    @admin.display(description="Car photo")
    def photo_info(self, obj):
        card = obj.photo_card
        if card:
            url = reverse("admin:core_rideoption_change", args=[card.pk])
            return format_html('{}<br>Photo comes from the <a href="{}">“{}”</a> card in 6. Fleet &amp; Rides – Cars. '
                               'Change it there.', image_preview(card.image, 100), url, card.name)
        url = reverse("admin:core_rideoption_changelist")
        return format_html('No photo yet. Upload it on a card in <a href="{}">6. Fleet &amp; Rides – Cars</a> '
                           'and choose this car in its “Linked car in booking popup” box.', url)

    @admin.display(description="Price")
    def price(self, obj):
        return f"{obj.price_display} {obj.price_suffix}"


@admin.register(TripRate)
class TripRateAdmin(admin.ModelAdmin):
    list_display = ("vehicle", "trip_type", "package", "price", "price_suffix", "extra_km_rate", "extra_hour_rate",
                    "is_active")
    list_display_links = ("vehicle",)
    list_editable = ("price", "price_suffix", "extra_km_rate", "extra_hour_rate", "is_active")
    list_filter = ("trip_type", "vehicle", "package")
    list_select_related = ("vehicle", "package")
    actions = [show_on_site, hide_from_site]
    fieldsets = (
        (None, {"fields": ("vehicle", "trip_type", "package")}),
        ("Price", {"fields": (("price", "price_suffix"), ("extra_km_rate", "extra_hour_rate"))}),
        ("Display", {"fields": ("is_active",)}),
    )


@admin.register(RentalPackage)
class RentalPackageAdmin(admin.ModelAdmin):
    list_display = ("name", "cars_priced", "order", "is_active")
    list_editable = ("order", "is_active")
    actions = [show_on_site, hide_from_site]

    @admin.display(description="Cars with a price")
    def cars_priced(self, obj):
        return obj.rates.count()


# ---------------------------------------------------------------------------
# 4. Fleet slider
# ---------------------------------------------------------------------------
@admin.register(FleetSection)
class FleetSectionAdmin(SingletonAdmin):
    fieldsets = (
        ("Heading", {
            "description": "The slides themselves are edited in “4. Fleet Slider – Slides”.",
            "fields": ("eyebrow", "title", "footer_text"),
        }),
        ("Slide movement", {"fields": ("autoplay", "autoplay_seconds")}),
    )


class FleetSpecInline(admin.TabularInline):
    model = FleetSpec
    extra = 0
    fields = ("label", "value", "order")


@admin.register(FleetSlide)
class FleetSlideAdmin(admin.ModelAdmin):
    formfield_overrides = SMALL_TEXTAREA
    inlines = [FleetSpecInline]
    list_display = ("thumb", "title", "tab_label", "order", "is_active")
    list_display_links = ("thumb", "title")
    list_editable = ("order", "is_active")
    actions = [show_on_site, hide_from_site]
    readonly_fields = ("image_preview",)
    list_select_related = ("ride_card",)
    fieldsets = (
        ("Tab (top right)", {"fields": ("tab_label", "tab_icon")}),
        ("Slide content", {
            "description": "The features row (Cabin Space, Luggage…) is edited in the table at the bottom.",
            "fields": ("badge_text", "title", "description"),
        }),
        ("Car photo", {"fields": ("ride_card", "image_preview", "image", "image_alt")}),
        ("Display", {"fields": ("order", "is_active")}),
    )

    @admin.display(description="Photo")
    def thumb(self, obj):
        return image_preview(obj.photo, 36)

    @admin.display(description="Photo shown on the website")
    def image_preview(self, obj):
        return image_preview(obj.photo, 100)


# ---------------------------------------------------------------------------
# 5. Stats
# ---------------------------------------------------------------------------
@admin.register(StatItem)
class StatItemAdmin(admin.ModelAdmin):
    list_display = ("preview", "number", "show_star", "label", "color", "order", "is_active")
    list_display_links = ("preview",)
    list_editable = ("number", "show_star", "label", "color", "order", "is_active")
    actions = [show_on_site, hide_from_site]
    fields = ("number", "show_star", "label", "color", "order", "is_active")

    @admin.display(description="Looks like")
    def preview(self, obj):
        colour = {"green": "#10844f", "dark": "#181c24", "navy": "#273b6b"}.get(obj.color, "#181c24")
        star = ' <span style="color:#f59e0b">★</span>' if obj.show_star else ""
        return format_html('<strong style="font-size:18px;color:{}">{}</strong>{}<br><small>{}</small>',
                           colour, obj.number, format_html(star), obj.label)


# ---------------------------------------------------------------------------
# 6. Fleet & Rides
# ---------------------------------------------------------------------------
@admin.register(RidesSection)
class RidesSectionAdmin(SingletonAdmin):
    fieldsets = (
        (None, {
            "description": "The car cards themselves are edited in “6. Fleet & Rides – Cars”.",
            "fields": ("badge_text", "title", "description", "side_badge_text"),
        }),
    )


@admin.register(RideOption)
class RideOptionAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": forms.Textarea(attrs={"rows": 4, "cols": 60})}}
    list_display = ("thumb", "name", "price", "badge_text", "is_featured", "order", "is_active")
    list_display_links = ("thumb", "name")
    list_editable = ("is_featured", "order", "is_active")
    actions = [show_on_site, hide_from_site]
    readonly_fields = ("image_preview",)
    fieldsets = (
        ("Car", {"fields": ("name", "subtitle", "description", "badge_text")}),
        ("Price", {"fields": (("currency_symbol", "base_price", "price_suffix"),)}),
        ("Car photo", {
            "description": "This photo is also shown in the booking popup for the linked car (see Button below).",
            "fields": ("image", "image_preview", "image_alt"),
        }),
        ("Features (small grey tags)", {"fields": ("features",)}),
        ("Button", {"fields": ("button_text", "booking_car", "is_featured")}),
        ("Display", {"fields": ("order", "is_active")}),
    )

    @admin.display(description="Photo")
    def thumb(self, obj):
        return image_preview(obj.image, 36)

    @admin.display(description="Current photo")
    def image_preview(self, obj):
        return image_preview(obj.image, 100)

    @admin.display(description="Price")
    def price(self, obj):
        return f"{obj.price_display} {obj.price_suffix}"


# ---------------------------------------------------------------------------
# 7. How It Works
# ---------------------------------------------------------------------------
@admin.register(StepsSection)
class StepsSectionAdmin(SingletonAdmin):
    fieldsets = (
        (None, {
            "description": "The step cards themselves are edited in “7. How It Works – Steps”.",
            "fields": ("badge_text", "title", "description", "step_word"),
        }),
        ("Green banner under the steps", {
            "fields": ("show_banner", "banner_title", "banner_text", "banner_badge"),
        }),
    )


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    formfield_overrides = SMALL_TEXTAREA
    list_display = ("title", "icon", "color", "highlight_text", "order", "is_active")
    list_editable = ("order", "is_active")
    actions = [show_on_site, hide_from_site]
    fieldsets = (
        ("Step card", {
            "description": "The step number (01, 02, 03…) follows the Position order automatically.",
            "fields": ("title", "description", "highlight_text"),
        }),
        ("Look", {"fields": (("icon", "color"),)}),
        ("Display", {"fields": ("order", "is_active")}),
    )


# ---------------------------------------------------------------------------
# 13. About Us
# ---------------------------------------------------------------------------
class AboutValueInline(admin.TabularInline):
    model = AboutValue
    extra = 0
    fields = ("icon", "title", "text", "order", "is_active")
    formfield_overrides = {models.CharField: {"widget": forms.TextInput(attrs={"size": 40})}}


@admin.register(AboutSection)
class AboutSectionAdmin(SingletonAdmin):
    inlines = [AboutValueInline]
    readonly_fields = ("image_preview",)
    fieldsets = (
        (None, {"fields": ("is_active", "badge_text", "title", "description")}),
        ("Services list", {"fields": ("services_heading", "services")}),
        ("Photo (optional)", {"fields": ("image", "image_preview", "image_alt")}),
        ("Mission, Vision & Why cards", {"fields": (("mission_title", "mission_text"),
                                                    ("vision_title", "vision_text"),
                                                    ("why_title", "why_text"))}),
        ("Values row", {"fields": ("values_heading",)}),
    )

    @admin.display(description="Current photo")
    def image_preview(self, obj):
        return image_preview(obj.image, 100)


# ---------------------------------------------------------------------------
# 8. Safety
# ---------------------------------------------------------------------------
@admin.register(SafetySection)
class SafetySectionAdmin(SingletonAdmin):
    fieldsets = (
        ("Left side", {
            "description": "The feature cards on the right are edited in “8. Safety – Feature Cards”.",
            "fields": ("badge_text", "title", "description"),
        }),
        ("Highlight box (under the paragraph)", {
            "fields": ("show_highlight", "highlight_title", "highlight_text", "highlight_tag"),
        }),
    )


@admin.register(SafetyFeature)
class SafetyFeatureAdmin(admin.ModelAdmin):
    formfield_overrides = SMALL_TEXTAREA
    list_display = ("title", "icon", "color", "order", "is_active")
    list_editable = ("order", "is_active")
    actions = [show_on_site, hide_from_site]
    fieldsets = (
        ("Card", {"fields": ("title", "subtitle", "description", "check_text")}),
        ("Look", {"fields": (("icon", "color"),)}),
        ("Display", {"fields": ("order", "is_active")}),
    )


# ---------------------------------------------------------------------------
# 9. Pricing
# ---------------------------------------------------------------------------
@admin.register(PricingSection)
class PricingSectionAdmin(SingletonAdmin):
    fieldsets = (
        (None, {
            "description": "The price cards themselves are edited in “9. Pricing – Plans”.",
            "fields": ("badge_text", "title", "description", "highlights"),
        }),
    )


@admin.register(PricingPlan)
class PricingPlanAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": forms.Textarea(attrs={"rows": 5, "cols": 60})}}
    list_display = ("title", "price", "car", "badge_text", "is_featured", "order", "is_active")
    list_editable = ("is_featured", "order", "is_active")
    list_select_related = ("car",)
    actions = [show_on_site, hide_from_site]
    readonly_fields = ("price_info",)
    fieldsets = (
        ("Plan", {"fields": ("title", "subtitle", ("icon", "color"), "badge_text")}),
        ("Price", {"fields": ("car", "price_info", "price_suffix", "description")}),
        ("Features", {"fields": ("features",)}),
        ("Button", {"fields": ("button_text", "is_featured")}),
        ("Display", {"fields": ("order", "is_active")}),
    )

    @admin.display(description="Price")
    def price(self, obj):
        return f"{obj.price_display} {obj.price_suffix}"

    @admin.display(description="Current price")
    def price_info(self, obj):
        if not obj.pk:
            return "Pick a linked car and save to see the price."
        url = reverse("admin:core_vehicleclass_change", args=[obj.car_id])
        return format_html('<strong style="font-size:16px">{}</strong> {}<br>To change it, edit '
                           '<a href="{}">{}</a> in 3. Booking Popup – Car Options.',
                           obj.price_display, obj.price_suffix, url, obj.car.name)


# ---------------------------------------------------------------------------
# 10. Testimonials
# ---------------------------------------------------------------------------
@admin.register(TestimonialsSection)
class TestimonialsSectionAdmin(SingletonAdmin):
    fieldsets = (
        (None, {
            "description": "The reviews themselves are edited in “10. Testimonials – Reviews”.",
            "fields": ("badge_text", "title", "description"),
        }),
    )


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": forms.Textarea(attrs={"rows": 4, "cols": 70})}}
    list_display = ("thumb", "name", "role", "rating", "short_quote", "order", "is_active")
    list_display_links = ("thumb", "name")
    list_editable = ("order", "is_active")
    actions = [show_on_site, hide_from_site]
    readonly_fields = ("photo_preview",)
    fieldsets = (
        ("Review", {"fields": ("rating", "quote")}),
        ("Customer", {"fields": ("name", ("role", "detail"), "is_verified", "photo", "photo_preview")}),
        ("Display", {"fields": ("order", "is_active")}),
    )

    @admin.display(description="Photo")
    def thumb(self, obj):
        return image_preview(obj.photo, 36)

    @admin.display(description="Current photo")
    def photo_preview(self, obj):
        return image_preview(obj.photo, 80)

    @admin.display(description="Review")
    def short_quote(self, obj):
        return obj.quote if len(obj.quote) <= 60 else obj.quote[:60] + "…"


# ---------------------------------------------------------------------------
# 11. FAQ
# ---------------------------------------------------------------------------
@admin.register(FAQSection)
class FAQSectionAdmin(SingletonAdmin):
    fieldsets = (
        ("Left side", {
            "description": "The questions themselves are edited in “11. FAQ – Questions”.",
            "fields": ("is_active", "badge_text", "title", "description"),
        }),
        ("“Still have questions?” box", {
            "fields": ("show_help_box", "help_title", "help_text", "help_button_text"),
        }),
    )


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": forms.Textarea(attrs={"rows": 5, "cols": 80})}}
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("question", "answer")
    actions = [show_on_site, hide_from_site]
    fields = ("question", "answer", "order", "is_active")


# ---------------------------------------------------------------------------
# 12. Footer
# ---------------------------------------------------------------------------
class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 0
    fields = ("platform", "link", "order", "is_active")


@admin.register(FooterSettings)
class FooterSettingsAdmin(SingletonAdmin):
    inlines = [SocialLinkInline]
    fieldsets = (
        ("Under the logo", {
            "description": "The footer uses the same logo as “1. Website Settings & Menu”. "
                           "Link columns (Company, Support, Legal) are edited in “12. Footer – Link Columns”.",
            "fields": ("tagline", "about_text", "highlights"),
        }),
        ("Address & contact", {"fields": ("company_name", "address", "map_link", "email",
                                          ("helpdesk_label", "helpdesk_phone"),
                                          ("landline_label", "landline_phone"))}),
        ("Bottom line", {"fields": ("copyright_text", "credit_text", "credit_link")}),
        ("Floating contact buttons (bottom-right corner)", {
            "description": "Round WhatsApp, Email and Call buttons that stay on screen while visitors scroll.",
            "fields": ("show_floating_buttons", "whatsapp_number", "whatsapp_message",
                       "show_email_button", "show_call_button"),
        }),
    )


class FooterLinkInline(admin.TabularInline):
    model = FooterLink
    extra = 0
    fields = ("label", "link", "order", "is_active", "open_in_new_tab")


@admin.register(FooterColumn)
class FooterColumnAdmin(admin.ModelAdmin):
    inlines = [FooterLinkInline]
    list_display = ("title", "link_names", "order", "is_active")
    list_editable = ("order", "is_active")
    fields = ("title", "order", "is_active")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("links")

    @admin.display(description="Links")
    def link_names(self, obj):
        return ", ".join(link.label for link in obj.links.all())


# ---------------------------------------------------------------------------
# Ride bookings received
# ---------------------------------------------------------------------------
@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ("ref", "created_at", "name", "phone", "trip_type", "pickup", "vehicle_name",
                    "when", "status", "email_sent")
    list_display_links = ("ref", "created_at")
    list_filter = ("status", "trip_type", "vehicle_name", "created_at")
    list_editable = ("status",)
    search_fields = ("name", "phone", "email", "pickup", "destination", "flight_number")
    readonly_fields = ("ref", "trip_type", "pickup", "destination", "scheduled_date", "scheduled_time",
                       "flight_number", "package_name", "num_days", "num_pax",
                       "date_option", "ride_window", "vehicle", "vehicle_name", "quoted_price", "extra_charges",
                       "name", "phone", "email", "ip_address", "email_sent", "created_at")
    fieldsets = (
        ("Customer", {"fields": ("ref", "name", "phone", "email")}),
        ("Trip", {"fields": ("trip_type", "pickup", "destination", ("scheduled_date", "scheduled_time"),
                             "flight_number", "package_name", ("num_days", "num_pax"))}),
        ("Car & fare", {"fields": ("vehicle_name", "quoted_price", "extra_charges")}),
        ("Follow-up", {"fields": ("status", "admin_notes")}),
        ("Other details", {"fields": ("created_at", "email_sent", "vehicle", "date_option", "ride_window",
                                      "ip_address"), "classes": ("collapse",)}),
    )

    @admin.display(description="Ref", ordering="pk")
    def ref(self, obj):
        return obj.reference

    @admin.display(description="Pickup date & time")
    def when(self, obj):
        if obj.scheduled_date:
            text = f"{obj.scheduled_date:%d %b}"
            return f"{text}, {obj.scheduled_time:%I:%M %p}" if obj.scheduled_time else text
        return obj.ride_window or obj.date_option or "Now"

    def has_add_permission(self, request):
        return False


# ---------------------------------------------------------------------------
# 14. Policy popups
# ---------------------------------------------------------------------------
@admin.register(LegalPage)
class LegalPageAdmin(admin.ModelAdmin):
    formfield_overrides = {models.TextField: {"widget": forms.Textarea(attrs={"rows": 18, "cols": 90})}}
    list_display = ("title", "footer_link", "updated_on", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "updated_on")}),
        ("Popup text", {"fields": ("intro", "content")}),
        ("Display", {"fields": ("order", "is_active")}),
    )

    @admin.display(description="Footer link “Goes to”")
    def footer_link(self, obj):
        return f"#{obj.slug}"
