from django import forms
from .models import FlightLogEntry
from .models import PilotProfile

class FlightLogEntryForm(forms.ModelForm):
    class Meta:
        model = FlightLogEntry

        # No duration fields here – they’re auto-calculated and non-editable.
        fields = [
            # Flight
            "date",
            "departure",
            "arrival",
            "off_block",
            "on_block",
            "pilot_role",

            # UAV / GCS
            "uav_type",
            "uav_reg",
            "engine_class",
            "gcs_type",
            "gcs_reg",

            # Times
            "connection_time",
            "engine_start",
            "takeoff",
            "landing",
            "engine_stop",
            "disconnection_time",

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

            "connection_time": forms.TimeInput(attrs={"type": "time"}),
            "engine_start": forms.TimeInput(attrs={"type": "time"}),
            "takeoff": forms.TimeInput(attrs={"type": "time"}),
            "landing": forms.TimeInput(attrs={"type": "time"}),
            "engine_stop": forms.TimeInput(attrs={"type": "time"}),
            "disconnection_time": forms.TimeInput(attrs={"type": "time"}),
        }
        
class PilotProfileForm(forms.ModelForm):
    class Meta:
        model = PilotProfile
        fields = [
            "profile_photo",
            "medical_certificate",
            "flight_crew_license",
            "other_document",
        ]
