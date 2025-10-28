from django.contrib import admin

from .models import Reservation, Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("name", "capacity", "location_description")
    search_fields = ("name", "location_description")


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ("name", "table", "date", "time", "party_size", "status")
    list_filter = ("status", "date", "table")
    search_fields = ("name", "email", "phone")
    autocomplete_fields = ("table", "user")
