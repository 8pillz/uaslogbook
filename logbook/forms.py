from django import forms

from .models import FlightLogEntry, PilotProfile


class FlightLogEntryForm(forms.ModelForm):
    class Meta:
        model = FlightLogEntry

        fields = [
            # Flight
            "date",
            "departure",
            "arrival",
            "off_block",
            "on_block",
            "pilot_role",

            # UAV / GCS (simple)
            "uav_type",
            "uav_model",
            "uav_reg",
            "gcs_type",
            "gcs_reg",

            # Advanced classification
            "uav_easa_class",
            "mission_type",
            "gcs_software",

            # Takeoffs / landings
            "takeoff_day",
            "takeoff_night",
            "landing_day",
            "landing_night",

            # Simulator & remarks
            "is_simulator",
            "simulator_type",
            "simulator_time",
            "remarks",
        ]

        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "off_block": forms.TimeInput(attrs={"type": "time"}),
            "on_block": forms.TimeInput(attrs={"type": "time"}),
        }


class PilotProfileForm(forms.ModelForm):
    class Meta:
        model = PilotProfile
        fields = [
            "profile_photo",
            "medical_certificate",
            "flight_crew_license",
            "other_document",
            "time_display_unit",
        ]

class PilotSettingsForm(forms.ModelForm):
    class Meta:
        model = PilotProfile
        fields = ["time_display_unit"]
