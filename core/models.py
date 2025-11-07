from django.db import models
from django.utils.translation import gettext_lazy as _


class RestaurantInfo(models.Model):
    """General information about the restaurant displayed across the site."""

    name = models.CharField(max_length=150, verbose_name=_("Название"))
    tagline = models.CharField(
        max_length=255, blank=True, verbose_name=_("Слоган")
    )
    description = models.TextField(verbose_name=_("Описание"))
    mission = models.TextField(blank=True, verbose_name=_("Миссия"))
    address = models.CharField(max_length=255, verbose_name=_("Адрес"))
    phone = models.CharField(max_length=30, verbose_name=_("Телефон"))
    email = models.EmailField(verbose_name=_("Электронная почта"))
    opening_hours = models.CharField(
        max_length=255, blank=True, verbose_name=_("Часы работы")
    )

    class Meta:
        verbose_name = _("Информация о ресторане")
        verbose_name_plural = _("Информация о ресторане")

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    """Services offered by the restaurant and shown on the landing page."""

    title = models.CharField(max_length=150, verbose_name=_("Название"))
    description = models.TextField(verbose_name=_("Описание"))
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Класс иконки Bootstrap"),
        verbose_name=_("Иконка"),
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name=_("Порядок отображения")
    )

    class Meta:
        ordering = ["order", "title"]
        verbose_name = _("Услуга")
        verbose_name_plural = _("Услуги")

    def __str__(self) -> str:
        return self.title


class TeamMember(models.Model):
    """Team members highlighted on the About page."""

    name = models.CharField(max_length=150, verbose_name=_("Имя"))
    role = models.CharField(max_length=150, verbose_name=_("Должность"))
    bio = models.TextField(blank=True, verbose_name=_("Биография"))
    photo_url = models.URLField(blank=True, verbose_name=_("Ссылка на фото"))
    order = models.PositiveIntegerField(
        default=0, verbose_name=_("Порядок отображения")
    )

    class Meta:
        ordering = ["order", "name"]
        verbose_name = _("Сотрудник")
        verbose_name_plural = _("Команда")

    def __str__(self) -> str:
        return f"{self.name} — {self.role}"


class ContactSubmission(models.Model):
    """Stores contact requests submitted from the website."""

    name = models.CharField(max_length=150, verbose_name=_("Имя"))
    email = models.EmailField(verbose_name=_("Электронная почта"))
    message = models.TextField(verbose_name=_("Сообщение"))
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Создано")
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Обращение")
        verbose_name_plural = _("Обращения")

    def __str__(self) -> str:
        return _("Сообщение от %(name)s") % {"name": self.name}
