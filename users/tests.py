from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from .forms import (
    BootstrapAuthenticationForm,
    BootstrapUserCreationForm,
    UserProfileForm,
    UserRegistrationForm,
)
from .models import CustomUser


class UserFormTests(TestCase):
    def test_registration_form_creates_user_with_unique_email(self):
        form = UserRegistrationForm(
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password1": "Complexpass123",
                "password2": "Complexpass123",
            }
        )
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(user.email, "new@example.com")

    def test_profile_form_updates_user(self):
        user = get_user_model().objects.create_user(
            username="profile",
            email="profile@example.com",
            password="pass1234",
        )
        form = UserProfileForm(
            data={"first_name": "Pro", "last_name": "File", "email": "p@e.com"},
            instance=user,
        )
        self.assertTrue(form.is_valid())
        form.save()
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Pro")
        self.assertEqual(user.email, "p@e.com")

    def test_bootstrap_forms_add_css_classes(self):
        auth_form = BootstrapAuthenticationForm()
        creation_form = BootstrapUserCreationForm()
        for form in (auth_form, creation_form):
            for field in form.fields.values():
                self.assertIn("form-control", field.widget.attrs.get("class", ""))


class UserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="viewer",
            email="viewer@example.com",
            password="pass1234",
        )

    def test_register_view_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "signup",
                "email": "signup@example.com",
                "password1": "Complexpass123",
                "password2": "Complexpass123",
            },
            follow=True,
        )
        self.assertTrue(get_user_model().objects.filter(username="signup").exists())
        self.assertEqual(response.request["PATH_INFO"], reverse("users:profile"))
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Welcome!", " ".join(messages))

    def test_profile_view_requires_login_and_updates_user(self):
        login = self.client.login(username="viewer", password="pass1234")
        self.assertTrue(login)
        response = self.client.post(
            reverse("users:profile"),
            {
                "first_name": "Vis",
                "last_name": "Itor",
                "email": "viewer@example.com",
            },
            follow=True,
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Vis")
        self.assertEqual(response.status_code, 200)
        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertIn("Profile updated successfully.", messages)

    def test_profile_view_includes_reservations_in_context(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("users:profile"))
        self.assertIn("reservations", response.context)
