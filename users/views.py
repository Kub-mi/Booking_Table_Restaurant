from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView

from reservations.models import Reservation

from .forms import UserProfileForm, UserRegistrationForm


class RegisterView(FormView):
    template_name = "users/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("users:profile")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Welcome! Your account has been created.")
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "users/profile.html"
    form_class = UserProfileForm
    success_url = reverse_lazy("users:profile")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reservations"] = (
            Reservation.objects.filter(user=self.request.user)
            .select_related("table")
            .order_by("-date", "-time")
        )
        return context

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Profile updated successfully.")
        return super().form_valid(form)

