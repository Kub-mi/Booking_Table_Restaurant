from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from .forms import ContactForm
from .models import RestaurantInfo, Service, TeamMember


class HomePageView(FormView):
    template_name = "core/home.html"
    form_class = ContactForm
    success_url = reverse_lazy("core:home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = RestaurantInfo.objects.first()
        context["services"] = Service.objects.all()
        context["team_members"] = TeamMember.objects.all()
        return context

    def form_valid(self, form):
        form.save()
        messages.success(
            self.request,
            "Спасибо! Мы свяжемся с вами в ближайшее время.",
        )
        return super().form_valid(form)


class AboutPageView(TemplateView):
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["restaurant"] = RestaurantInfo.objects.first()
        context["team_members"] = TeamMember.objects.all()
        return context
