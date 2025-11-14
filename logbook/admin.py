from django.contrib import admin
from .models import FlightLogEntry

@admin.register(FlightLogEntry)
class FlightLogEntryAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "uav_type",
        "uav_reg",
        "departure",
        "arrival",
        "flight_time",
        "block_time",
        "engine_time",
        "gcs_time",
        "pilot_role",
        "user",
    )
    list_filter = ("uav_type", "date", "pilot_role")
