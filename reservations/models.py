from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Table(models.Model):
    """Информация о столе в ресторане."""
    number = models.PositiveIntegerField(unique=True, verbose_name="Номер стола")
    seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Количество мест"
    )
    description = models.CharField(max_length=255, blank=True, verbose_name="Описание")

    class Meta:
        ordering = ["number"]
        verbose_name = "Стол"
        verbose_name_plural = "Столы"

    def __str__(self):
        return f"Стол #{self.number} ({self.seats} мест)"


class Booking(models.Model):
    """Бронирование столика пользователем."""
    STATUS_CHOICES = [
        ("new", "Новое"),
        ("confirmed", "Подтверждено"),
        ("cancelled", "Отменено"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Пользователь"
    )
    table = models.ForeignKey(
        Table,
        on_delete=models.CASCADE,
        related_name="bookings",
        verbose_name="Стол"
    )
    guests = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Количество гостей"
    )
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Начало")
    end_time = models.TimeField(verbose_name="Окончание")
    comment = models.CharField(max_length=255, blank=True, verbose_name="Комментарий")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="new", verbose_name="Статус"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ["-date", "-start_time"]
        indexes = [models.Index(fields=["date", "start_time", "end_time", "table"])]
        verbose_name = "Бронь"
        verbose_name_plural = "Брони"

    def __str__(self):
        return f"{self.user} | {self.table} | {self.date} {self.start_time}-{self.end_time}"