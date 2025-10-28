from django.db import models


class RestaurantInfo(models.Model):
    """General information about the restaurant displayed across the site."""

    name = models.CharField(max_length=150)
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    mission = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    email = models.EmailField()
    opening_hours = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Restaurant information"
        verbose_name_plural = "Restaurant information"

    def __str__(self) -> str:
        return self.name


class Service(models.Model):
    """Services offered by the restaurant and shown on the landing page."""

    title = models.CharField(max_length=150)
    description = models.TextField()
    icon = models.CharField(max_length=100, blank=True, help_text="Bootstrap icon class")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self) -> str:
        return self.title


class TeamMember(models.Model):
    """Team members highlighted on the About page."""

    name = models.CharField(max_length=150)
    role = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    photo_url = models.URLField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self) -> str:
        return f"{self.name} — {self.role}"


class ContactSubmission(models.Model):
    """Stores contact requests submitted from the website."""

    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Message from {self.name}"
