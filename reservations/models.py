from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class Table(models.Model):
    """Representation of a table that can be reserved in the restaurant."""

    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    location_description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Столик"
        verbose_name_plural = "Столики"

    def __str__(self) -> str:
        return f"{self.name} ({self.capacity} гостей)"


class ReservationQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=Reservation.Status.CANCELLED)

    def upcoming(self):
        now = timezone.localtime()
        return self.active().filter(date__gte=now.date())


class Reservation(models.Model):
    """A reservation made for a specific table and time slot."""

    class Status(models.TextChoices):
        PENDING = "pending", "В ожидании"
        CONFIRMED = "confirmed", "Подтверждено"
        CANCELLED = "cancelled", "Отменено"

    table = models.ForeignKey(Table, related_name="reservations", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reservations",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    date = models.DateField()
    time = models.TimeField()
    party_size = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ReservationQuerySet.as_manager()

    class Meta:
        ordering = ["-date", "-time"]
        constraints = [
            models.UniqueConstraint(
                fields=["table", "date", "time"],
                condition=~models.Q(status="cancelled"),
                name="unique_active_table_booking",
            )
        ]
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"

    def __str__(self) -> str:
        return f"Бронирование для {self.name} на {self.date} в {self.time}"

    def clean(self) -> None:
        super().clean()
        if self.party_size > self.table.capacity:
            raise ValidationError(
                {"party_size": "Количество гостей превышает вместимость столика."}
            )

        if self.date < timezone.localdate():
            raise ValidationError({"date": "Нельзя выбрать прошедшую дату."})

    def cancel(self) -> None:
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])
