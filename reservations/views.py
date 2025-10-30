from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from .forms import ReservationForm
from .models import Reservation, Table


class ReservationCreateView(LoginRequiredMixin, CreateView):
    template_name = "reservations/reservation_form.html"
    form_class = ReservationForm
    success_url = reverse_lazy("reservations:list")

    def get_available_tables(self):
        parsed_date, parsed_time, party_size = ReservationForm.parse_filters(
            self.request.POST if self.request.method == "POST" else self.request.GET
        )

        tables = Table.objects.all()
        if party_size:
            tables = tables.filter(capacity__gte=party_size)

        if parsed_date and parsed_time:
            unavailable_ids = (
                Reservation.objects.active()
                .filter(date=parsed_date, time=parsed_time)
                .values_list("table_id", flat=True)
            )
            tables = tables.exclude(id__in=unavailable_ids)

        return tables

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["available_tables"] = self.get_available_tables()
        return kwargs

    def form_valid(self, form):
        reservation = form.save(commit=False)
        reservation.user = self.request.user
        reservation.full_clean()
        reservation.save()
        messages.success(
            self.request,
            "Запрос на бронирование успешно отправлен.",
        )
        self.object = reservation
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        data = self.request.POST if self.request.method == "POST" else self.request.GET
        context["available_tables"] = self.get_available_tables()
        context["filters"] = {
            "date": data.get("date", ""),
            "time": data.get("time", ""),
            "party_size": data.get("party_size", ""),
        }
        return context


class ReservationListView(LoginRequiredMixin, ListView):
    template_name = "reservations/reservation_list.html"
    context_object_name = "reservations"

    def get_queryset(self):
        return (
            Reservation.objects.filter(user=self.request.user)
            .select_related("table")
            .order_by("-date", "-time")
        )


class ReservationUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "reservations/reservation_update.html"
    model = Reservation
    form_class = ReservationForm
    success_url = reverse_lazy("reservations:list")

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        kwargs["available_tables"] = Table.objects.all()
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Бронирование успешно обновлено.")
        return super().form_valid(form)


class ReservationCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        reservation = Reservation.objects.filter(
            pk=kwargs.get("pk"), user=request.user
        ).first()
        if not reservation:
            messages.error(request, "Бронирование не найдено.")
            return HttpResponseRedirect(reverse("reservations:list"))

        if reservation.status == Reservation.Status.CANCELLED:
            messages.info(request, "Бронирование уже отменено.")
        else:
            reservation.cancel()
            messages.success(request, "Бронирование отменено.")

        return HttpResponseRedirect(reverse("reservations:list"))
