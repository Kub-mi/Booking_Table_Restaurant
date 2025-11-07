from django import forms
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_time

from .models import Reservation, Table


class ReservationForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"})
    )
    time = forms.TimeField(
        widget=forms.TimeInput(attrs={"type": "time", "class": "form-control"})
    )

    class Meta:
        model = Reservation
        fields = [
            "table",
            "name",
            "email",
            "phone",
            "date",
            "time",
            "party_size",
            "notes",
        ]
        widgets = {
            "table": forms.Select(attrs={"class": "form-select"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "party_size": forms.NumberInput(
                attrs={"class": "form-control", "min": 1, "max": 20}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        available_tables = kwargs.pop("available_tables", None)
        super().__init__(*args, **kwargs)
        self.fields["table"].queryset = available_tables or Table.objects.all()
        self.fields["table"].empty_label = "Select a table"

        if self.user and self.user.is_authenticated:
            self.fields["name"].initial = self.user.get_full_name() or self.user.username
            self.fields["email"].initial = self.user.email

    def clean(self):
        cleaned_data = super().clean()
        table = cleaned_data.get("table")
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        if date and date < timezone.localdate():
            raise forms.ValidationError("Reservations cannot be made for past dates.")

        if table and date and time:
            conflicts = (
                Reservation.objects.active()
                .filter(table=table, date=date, time=time)
                .exclude(pk=self.instance.pk)
            )
            if conflicts.exists():
                raise forms.ValidationError(
                    "The selected table is not available for the chosen time."
                )

        party_size = cleaned_data.get("party_size")
        if table and party_size and party_size > table.capacity:
            self.add_error(
                "party_size", "Selected table cannot accommodate your party size."
            )

        return cleaned_data

    @staticmethod
    def parse_filters(data):
        """Utility used by the view to build availability filters."""

        date_str = data.get("date")
        time_str = data.get("time")
        party_size = data.get("party_size")

        parsed_date = parse_date(date_str) if date_str else None
        parsed_time = parse_time(time_str) if time_str else None

        try:
            parsed_party = int(party_size) if party_size else None
        except (TypeError, ValueError):
            parsed_party = None

        return parsed_date, parsed_time, parsed_party
