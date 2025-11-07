from datetime import timedelta

from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ContactForm
from .models import ContactSubmission, RestaurantInfo, Service, TeamMember


class HomePageViewTests(TestCase):
    def setUp(self):
        self.restaurant = RestaurantInfo.objects.create(
            name="Testaurant",
            tagline="Best in town",
            description="A cozy place.",
            mission="Serve joy",
            address="123 Test St",
            phone="1234567890",
            email="info@test.com",
            opening_hours="Always",
        )
        Service.objects.create(title="Delivery", description="Fast", order=1)
        TeamMember.objects.create(name="Alice", role="Chef", order=1)
        self.client = Client()

    def test_home_page_context_contains_content(self):
        response = self.client.get(reverse("core:home"))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], ContactForm)
        self.assertEqual(response.context["restaurant"], self.restaurant)
        self.assertEqual(list(response.context["services"])[0].title, "Delivery")
        self.assertEqual(list(response.context["team_members"])[0].name, "Alice")

    def test_submit_contact_form_creates_submission(self):
        payload = {
            "name": "Bob",
            "email": "bob@example.com",
            "message": "Hello!",
        }
        response = self.client.post(reverse("core:home"), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        submission = ContactSubmission.objects.get()
        self.assertEqual(submission.name, "Bob")
        messages = [message.message for message in get_messages(response.wsgi_request)]
        self.assertIn(
            "Спасибо! Мы свяжемся с вами в ближайшее время.",
            " ".join(messages),
        )


class AboutPageViewTests(TestCase):
    def test_about_page_uses_restaurant_data(self):
        restaurant = RestaurantInfo.objects.create(
            name="Future Foods",
            tagline="",
            description="Modern.",
            mission="Innovate",
            address="789 Future Rd",
            phone="9876543210",
            email="future@example.com",
            opening_hours="Weekdays",
        )
        member = TeamMember.objects.create(name="Eve", role="Manager", order=2)
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["restaurant"], restaurant)
        self.assertIn(member, response.context["team_members"])


class ContactFormTests(TestCase):
    def test_contact_form_saves_submission(self):
        form = ContactForm(
            data={"name": "Sam", "email": "sam@example.com", "message": "Need info"}
        )
        self.assertTrue(form.is_valid())
        instance = form.save()
        self.assertEqual(ContactSubmission.objects.count(), 1)
        self.assertEqual(instance.message, "Need info")
        self.assertLessEqual(
            timezone.now() - instance.created_at,
            timedelta(seconds=5),
        )
