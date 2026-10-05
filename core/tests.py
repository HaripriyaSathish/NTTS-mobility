from datetime import time, timedelta
from decimal import Decimal
from unittest import mock

from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import BookingForm
from .models import BookingRequest, RentalPackage, SMTPSettings, TripRate, VehicleClass
from .utils import send_booking_emails


class BookingTestData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.sedan = VehicleClass.objects.create(name="Test Sedan", button_name="Test Sedan", details="4+1",
                                                base_price=Decimal("80"), seats=4, order=1)
        cls.suv = VehicleClass.objects.create(name="Test SUV", button_name="Test SUV", details="7+1",
                                              base_price=Decimal("200"), seats=7, order=2)
        cls.package = RentalPackage.objects.create(name="4 Hrs / 40 Km", order=1)
        cls.airport = TripRate.objects.create(vehicle=cls.sedan, trip_type="airport", price=Decimal("1200"),
                                              price_suffix="fixed", extra_km_rate=Decimal("14"))
        cls.local = TripRate.objects.create(vehicle=cls.sedan, trip_type="local", package=cls.package,
                                            price=Decimal("1100"), extra_km_rate=Decimal("14"),
                                            extra_hour_rate=Decimal("150"))
        cls.out_sedan = TripRate.objects.create(vehicle=cls.sedan, trip_type="outstation", price=Decimal("3500"),
                                                price_suffix="per day (250 Km)")
        cls.out_suv = TripRate.objects.create(vehicle=cls.suv, trip_type="outstation", price=Decimal("5500"),
                                              price_suffix="per day (250 Km)")

    def data(self, trip="airport", **extra):
        tomorrow = timezone.localdate() + timedelta(days=1)
        base = {
            "trip_type": trip, "pickup": "12 Anna Nagar, Chennai", "scheduled_date": tomorrow.isoformat(),
            "scheduled_time": "10:30", "name": "Priya Raj", "phone": "9876543210", "email": "priya@gmail.com",
        }
        if trip == "airport":
            base.update(destination="Chennai International Airport", flight_number="6e2134", rate=self.airport.pk)
        elif trip == "local":
            base.update(rate=self.local.pk)
        else:
            base.update(num_days="2", num_pax="3", rate=self.out_sedan.pk)
        base.update(extra)
        return base


class BookingFormTests(BookingTestData):
    def errors(self, **kwargs):
        form = BookingForm(self.data(**kwargs))
        form.is_valid()
        return form.errors

    def test_valid_airport_local_outstation(self):
        for trip in ("airport", "local", "outstation"):
            form = BookingForm(self.data(trip))
            self.assertTrue(form.is_valid(), (trip, form.errors))

    def test_flight_number_is_formatted(self):
        form = BookingForm(self.data(flight_number="ai-202"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["flight_number"], "AI 202")

    def test_airport_needs_drop_and_flight(self):
        errors = self.errors(destination="", flight_number="")
        self.assertIn("destination", errors)
        self.assertIn("flight_number", errors)

    def test_bad_flight_numbers(self):
        for value in ("12345", "A", "AIRINDIA", "6E 21345"):
            self.assertIn("flight_number", self.errors(flight_number=value), value)

    def test_drop_same_as_pickup(self):
        self.assertIn("destination", self.errors(destination="12 anna nagar, chennai"))

    def test_bad_addresses(self):
        for value in ("", "   ", "12", "<script>", "a$b@c!"):
            self.assertIn("pickup", self.errors(pickup=value), value)

    def test_date_and_time_rules(self):
        today = timezone.localdate()
        self.assertIn("scheduled_date", self.errors(scheduled_date=""))
        self.assertIn("scheduled_date", self.errors(scheduled_date=(today - timedelta(days=1)).isoformat()))
        self.assertIn("scheduled_date", self.errors(scheduled_date=(today + timedelta(days=91)).isoformat()))
        self.assertIn("scheduled_time", self.errors(scheduled_time=""))
        soon = timezone.localtime() + timedelta(minutes=5)
        if soon.date() == today:  # pickup 5 minutes from now is too soon
            self.assertIn("scheduled_time", self.errors(scheduled_date=today.isoformat(),
                                                        scheduled_time=soon.strftime("%H:%M")))

    def test_outstation_days_and_pax(self):
        for value in ("", "0", "31", "two", "1.5"):
            self.assertIn("num_days", self.errors(trip="outstation", num_days=value), value)
        for value in ("", "0", "21", "x"):
            self.assertIn("num_pax", self.errors(trip="outstation", num_pax=value), value)

    def test_too_many_pax_for_car(self):
        self.assertIn("rate", self.errors(trip="outstation", num_pax="6"))
        form = BookingForm(self.data("outstation", num_pax="6", rate=self.out_suv.pk))
        self.assertTrue(form.is_valid(), form.errors)

    def test_car_must_match_tab(self):
        self.assertIn("rate", self.errors(trip="local", rate=self.airport.pk))
        self.assertIn("rate", self.errors(rate=""))

    def test_hidden_price_or_package_is_rejected(self):
        TripRate.objects.filter(pk=self.local.pk).update(is_active=False)
        self.assertIn("rate", self.errors(trip="local"))
        TripRate.objects.filter(pk=self.local.pk).update(is_active=True)
        RentalPackage.objects.filter(pk=self.package.pk).update(is_active=False)
        self.assertIn("rate", self.errors(trip="local"))

    def test_bad_trip_type(self):
        self.assertIn("trip_type", self.errors(trip_type="space"))

    def test_other_tab_fields_are_dropped(self):
        form = BookingForm(self.data("local", destination="Airport", flight_number="6E 1", num_days="3"))
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["destination"], "")
        self.assertEqual(form.cleaned_data["flight_number"], "")
        self.assertIsNone(form.cleaned_data["num_days"])


class BookRideViewTests(BookingTestData):
    def post(self, data):
        with mock.patch("core.views.threading.Thread"):  # no real email in tests
            return self.client.post(reverse("book_ride"), data)

    def test_saves_outstation_booking(self):
        res = self.post(self.data("outstation", num_days="3", num_pax="2"))
        self.assertEqual(res.status_code, 200, res.content)
        booking = BookingRequest.objects.get()
        self.assertEqual(booking.trip_type, "outstation")
        self.assertEqual((booking.num_days, booking.num_pax), (3, 2))
        self.assertEqual(booking.quoted_price, "₹3,500 per day (250 Km)")
        self.assertEqual(booking.vehicle_name, "Test Sedan")

    def test_saves_local_booking_with_package(self):
        res = self.post(self.data("local"))
        self.assertEqual(res.status_code, 200, res.content)
        booking = BookingRequest.objects.get()
        self.assertEqual(booking.package_name, "4 Hrs / 40 Km")
        self.assertEqual(booking.extra_charges, "₹14/Km · ₹150/hour")

    def test_errors_returned_as_json(self):
        res = self.post(self.data(flight_number="", phone="12345"))
        self.assertEqual(res.status_code, 400)
        errors = res.json()["errors"]
        self.assertIn("flight_number", errors)
        self.assertIn("phone", errors)
        self.assertFalse(BookingRequest.objects.exists())


class BookingEmailTests(BookingTestData):
    def test_admin_and_customer_emails(self):
        SMTPSettings.objects.create(username="x@gmail.com", password="x", from_email="New Track <x@gmail.com>",
                                    receiver_email="team@example.com")
        booking = BookingRequest.objects.create(
            trip_type="airport", pickup="12 Anna Nagar", destination="Chennai Airport", ride_type="schedule",
            scheduled_date=timezone.localdate() + timedelta(days=1), scheduled_time=time(10, 30),
            flight_number="6E 2134", vehicle=self.sedan, vehicle_name="Test Sedan", quoted_price="₹1,200 fixed",
            extra_charges="₹14/Km", name="Priya Raj", phone="+91 98765 43210", email="priya@gmail.com",
        )
        with mock.patch("core.utils.get_connection", return_value=mail.get_connection(
                "django.core.mail.backends.locmem.EmailBackend")):
            send_booking_emails(booking)
        self.assertEqual(len(mail.outbox), 2)
        admin_mail, customer_mail = mail.outbox
        self.assertEqual(admin_mail.to, ["team@example.com"])
        self.assertIn(booking.reference, admin_mail.subject)
        self.assertIn("Airport Transfer", admin_mail.subject)
        for msg in (admin_mail, customer_mail):
            html = msg.alternatives[0][0]
            for text in ("6E 2134", "Chennai Airport", "₹1,200 fixed", "Test Sedan"):
                self.assertIn(text, msg.body)
                self.assertIn(text, html)
        self.assertIn("tel:+919876543210", admin_mail.alternatives[0][0])
        self.assertEqual(customer_mail.to, ["priya@gmail.com"])
