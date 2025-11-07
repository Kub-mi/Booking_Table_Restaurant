from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.core.exceptions import ValidationError
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ReservationForm
from .models import Reservation, Table
from .views import ReservationCreateView


class ReservationModelTests(TestCase):
    def setUp(self):
        self.table = Table.objects.create(name="T1", capacity=4)
        self.date = timezone.localdate() + timedelta(days=1)
        self.time = (timezone.now() + timedelta(hours=2)).time().replace(microsecond=0)

    def test_str_representation(self):
        reservation = Reservation.objects.create(
            table=self.table,
            name="John",
            email="john@example.com",
            phone="000",
            date=self.date,
            time=self.time,
            party_size=2,
        )
        self.assertIn("Reservation for John", str(reservation))

    def test_clean_validates_party_size(self):
        reservation = Reservation(
            table=self.table,
            name="Big Group",
            email="big@example.com",
            phone="111",
            date=self.date,
            time=self.time,
            party_size=10,
        )
        with self.assertRaisesMessage(
            ValidationError, "Party size exceeds table capacity."
        ):
            reservation.full_clean()

    def test_clean_rejects_past_dates(self):
        reservation = Reservation(
            table=self.table,
            name="Past",
            email="past@example.com",
            phone="222",
            date=self.date - timedelta(days=5),
            time=self.time,
            party_size=2,
        )
        with self.assertRaisesMessage(
            ValidationError, "Reservation date cannot be in the past."
        ):
            reservation.full_clean()

    def test_cancel_updates_status(self):
        reservation = Reservation.objects.create(
            table=self.table,
            name="Jane",
            email="jane@example.com",
            phone="333",
            date=self.date,
            time=self.time,
            party_size=2,
        )
        reservation.cancel()
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.CANCELLED)

    def test_queryset_helpers(self):
        cancelled = Reservation.objects.create(
            table=self.table,
            name="Cancelled",
            email="cancel@example.com",
            phone="444",
            date=self.date,
            time=self.time,
            party_size=2,
            status=Reservation.Status.CANCELLED,
        )
        upcoming = Reservation.objects.create(
            table=self.table,
            name="Upcoming",
            email="up@example.com",
            phone="555",
            date=self.date + timedelta(days=2),
            time=self.time,
            party_size=2,
        )
        self.assertNotIn(cancelled, Reservation.objects.active())
        self.assertIn(upcoming, Reservation.objects.upcoming())


class ReservationFormTests(TestCase):
    def setUp(self):
        self.table = Table.objects.create(name="Family", capacity=6)
        self.user = get_user_model().objects.create_user(
            username="tester", email="tester@example.com", password="pass1234"
        )

    def _future_date(self):
        return timezone.localdate() + timedelta(days=1)

    def _future_time(self):
        return (timezone.now() + timedelta(hours=3)).time().replace(microsecond=0)

    def test_initial_data_prefilled_for_authenticated_user(self):
        form = ReservationForm(user=self.user)
        self.assertEqual(form.fields["name"].initial, "tester")
        self.assertEqual(form.fields["email"].initial, "tester@example.com")

    def test_clean_detects_conflict_and_party_size(self):
        existing = Reservation.objects.create(
            table=self.table,
            name="Existing",
            email="ex@example.com",
            phone="000",
            date=self._future_date(),
            time=self._future_time(),
            party_size=4,
        )
        form = ReservationForm(
            data={
                "table": self.table.pk,
                "name": "New",
                "email": "new@example.com",
                "phone": "123",
                "date": existing.date,
                "time": existing.time,
                "party_size": 7,
                "notes": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn(
            "The selected table is not available for the chosen time.",
            form.non_field_errors(),
        )
        self.assertIn("party_size", form.errors)
        self.assertIn("Party size", form.errors["party_size"][0])

    def test_parse_filters_handles_invalid_values(self):
        date, time, party = ReservationForm.parse_filters({
            "date": "not-a-date",
            "time": "not-a-time",
            "party_size": "oops",
        })
        self.assertIsNone(date)
        self.assertIsNone(time)
        self.assertIsNone(party)


class ReservationViewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="viewer", email="viewer@example.com", password="pass1234"
        )
        self.client.force_login(self.user)
        self.table_small = Table.objects.create(name="Two", capacity=2)
        self.table_large = Table.objects.create(name="Six", capacity=6)
        self.future_date = timezone.localdate() + timedelta(days=2)
        self.future_time = (timezone.now() + timedelta(hours=4)).time().replace(
            microsecond=0
        )

    def test_get_available_tables_filters_by_party_size_and_conflicts(self):
        Reservation.objects.create(
            table=self.table_large,
            name="Block",
            email="block@example.com",
            phone="123",
            date=self.future_date,
            time=self.future_time,
            party_size=4,
        )
        request = self.factory.get(
            reverse("reservations:create"),
            {
                "party_size": 4,
                "date": str(self.future_date),
                "time": str(self.future_time),
            },
        )
        request.user = self.user
        view = ReservationCreateView()
        view.setup(request)
        queryset = view.get_available_tables()
        self.assertNotIn(self.table_small, queryset)
        self.assertNotIn(self.table_large, queryset)

    def test_form_submission_creates_reservation_and_sets_message(self):
        response = self.client.post(
            reverse("reservations:create"),
            {
                "table": self.table_large.pk,
                "name": "Viewer",
                "email": "viewer@example.com",
                "phone": "555",
                "date": self.future_date,
                "time": self.future_time,
                "party_size": 3,
                "notes": "Window",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        reservation = Reservation.objects.get()
        self.assertEqual(reservation.user, self.user)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Reservation request submitted successfully.", messages)

    def test_list_view_returns_user_reservations(self):
        other = get_user_model().objects.create_user(
            username="other", email="other@example.com", password="pass1234"
        )
        Reservation.objects.create(
            table=self.table_large,
            user=self.user,
            name="Mine",
            email="mine@example.com",
            phone="123",
            date=self.future_date,
            time=self.future_time,
            party_size=2,
        )
        Reservation.objects.create(
            table=self.table_large,
            user=other,
            name="Theirs",
            email="theirs@example.com",
            phone="999",
            date=self.future_date,
            time=(timezone.datetime.combine(
                self.future_date, self.future_time
            )
            + timedelta(minutes=30)).time(),
            party_size=2,
        )
        response = self.client.get(reverse("reservations:list"))
        self.assertEqual(len(response.context["reservations"]), 1)
        self.assertEqual(response.context["reservations"][0].name, "Mine")

    def test_update_view_allows_editing(self):
        reservation = Reservation.objects.create(
            table=self.table_large,
            user=self.user,
            name="Edit",
            email="edit@example.com",
            phone="777",
            date=self.future_date,
            time=self.future_time,
            party_size=2,
        )
        self.client.post(
            reverse("reservations:update", args=[reservation.pk]),
            {
                "table": self.table_large.pk,
                "name": "Edited",
                "email": "viewer@example.com",
                "phone": "888",
                "date": self.future_date,
                "time": self.future_time,
                "party_size": 2,
                "notes": "",
            },
            follow=True,
        )
        reservation.refresh_from_db()
        self.assertEqual(reservation.name, "Edited")

    def test_update_view_sets_success_message(self):
        reservation = Reservation.objects.create(
            table=self.table_large,
            user=self.user,
            name="Message",
            email="message@example.com",
            phone="123",
            date=self.future_date,
            time=self.future_time,
            party_size=2,
        )
        response = self.client.post(
            reverse("reservations:update", args=[reservation.pk]),
            {
                "table": self.table_large.pk,
                "name": "Message",
                "email": "viewer@example.com",
                "phone": "123",
                "date": self.future_date,
                "time": self.future_time,
                "party_size": 2,
                "notes": "",
            },
            follow=True,
        )
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Reservation updated successfully.", messages)

    def test_cancel_view_handles_missing_reservation_and_success(self):
        response = self.client.post(reverse("reservations:cancel", args=[999]), follow=True)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Reservation not found.", messages)

        reservation = Reservation.objects.create(
            table=self.table_large,
            user=self.user,
            name="Cancel",
            email="cancel@example.com",
            phone="000",
            date=self.future_date,
            time=self.future_time,
            party_size=2,
        )
        response = self.client.post(
            reverse("reservations:cancel", args=[reservation.pk]), follow=True
        )
        reservation.refresh_from_db()
        self.assertEqual(reservation.status, Reservation.Status.CANCELLED)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Reservation cancelled.", messages)

    def test_cancel_view_reports_already_cancelled(self):
        reservation = Reservation.objects.create(
            table=self.table_large,
            user=self.user,
            name="Cancelled",
            email="cancelled@example.com",
            phone="555",
            date=self.future_date,
            time=self.future_time,
            party_size=2,
            status=Reservation.Status.CANCELLED,
        )
        response = self.client.post(
            reverse("reservations:cancel", args=[reservation.pk]), follow=True
        )
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Reservation is already cancelled.", messages)
