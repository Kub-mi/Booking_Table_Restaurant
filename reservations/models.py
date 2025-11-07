from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Table(models.Model):
    """Representation of a table that can be reserved in the restaurant."""

    name = models.CharField(
        max_length=100, unique=True, verbose_name=_("Название")
    )
    capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name=_("Количество мест"),
    )
    location_description = models.CharField(
        max_length=255, blank=True, verbose_name=_("Описание расположения")
    )

    class Meta:
        ordering = ["name"]
        verbose_name = _("Стол")
        verbose_name_plural = _("Столы")

    def __str__(self) -> str:
        return _("%(name)s (%(capacity)s гостей)") % {
            "name": self.name,
            "capacity": self.capacity,
        }


class ReservationQuerySet(models.QuerySet):
    def active(self):
        return self.exclude(status=Reservation.Status.CANCELLED)

    def upcoming(self):
        now = timezone.localtime()
        return self.active().filter(date__gte=now.date())


class Reservation(models.Model):
    """A reservation made for a specific table and time slot."""

    class Status(models.TextChoices):
        PENDING = "pending", _("В ожидании")
        CONFIRMED = "confirmed", _("Подтверждена")
        CANCELLED = "cancelled", _("Отменена")

    table = models.ForeignKey(Table, related_name="reservations", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reservations",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=150, verbose_name=_("Имя"))
    email = models.EmailField(verbose_name=_("Электронная почта"))
    phone = models.CharField(max_length=30, verbose_name=_("Телефон"))
    date = models.DateField(verbose_name=_("Дата"))
    time = models.TimeField(verbose_name=_("Время"))
    party_size = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name=_("Количество гостей"),
    )
    notes = models.TextField(blank=True, verbose_name=_("Комментарий"))
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Статус"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Создано")
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))

    objects = ReservationQuerySet.as_manager()

    class Meta:
        ordering = ["-date", "-time"]
        verbose_name = _("Бронирование")
        verbose_name_plural = _("Бронирования")
        constraints = [
            models.UniqueConstraint(
                fields=["table", "date", "time"],
                condition=~models.Q(status="cancelled"),
                name="unique_active_table_booking",
            )
        ]

    def __str__(self) -> str:
        return _("Бронирование для %(name)s %(date)s в %(time)s") % {
            "name": self.name,
            "date": self.date,
            "time": self.time,
        }

    def clean(self) -> None:
        super().clean()
        if self.party_size > self.table.capacity:
            raise ValidationError(
                {"party_size": _("Количество гостей превышает вместимость стола.")}
            )

        if self.date < timezone.localdate():
            raise ValidationError(
                {"date": _("Дата бронирования не может быть в прошлом.")}
            )

    def cancel(self) -> None:
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status", "updated_at"])
