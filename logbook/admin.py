from django.contrib import admin
from .models import FlightLogEntry, PilotProfile


@admin.register(FlightLogEntry)
class FlightLogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "uav_type",
        "uav_model",
        "uav_reg",
        "departure",
        "arrival",
        "flight_time",
    )
    list_filter = (
        "uav_type",
        "mission_type",
        "pilot_role",
        "is_simulator",
        "date",
    )
    search_fields = (
        "uav_model",
        "uav_reg",
        "departure",
        "arrival",
        "remarks",
    )
    ordering = ("-date", "-created_at")


@admin.register(PilotProfile)
class PilotProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "updated_at")
