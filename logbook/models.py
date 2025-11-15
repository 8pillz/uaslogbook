from datetime import datetime

from django.conf import settings
from django.db import models


class PilotProfile(models.Model):
    class TimeDisplayUnit(models.TextChoices):
        MINUTES = "MIN", "Minutes"
        HHMM = "HMM", "Hours:Minutes (hh:mm)"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pilot_profile",
    )

    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )

    medical_certificate = models.FileField(
        "Medical certificate (PDF)",
        upload_to="documents/",
        blank=True,
        null=True,
    )

    flight_crew_license = models.FileField(
        "Flight crew license (PDF)",
        upload_to="documents/",
        blank=True,
        null=True,
    )

    other_document = models.FileField(
        "Other document",
        upload_to="documents/",
        blank=True,
        null=True,
    )

    time_display_unit = models.CharField(
        "Time display unit",
        max_length=3,
        choices=TimeDisplayUnit.choices,
        default=TimeDisplayUnit.MINUTES,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile for {self.user}"

class FlightLogEntry(models.Model):
    class PilotRole(models.TextChoices):
        PIC = "PIC", "Pilot in Command"
        COPILOT = "COP", "Co-pilot"
        OBSERVER = "OBS", "Observer / VO"
        STUDENT = "STU", "Student / Trainee"
        INSTRUCTOR = "INS", "Instructor"
        EXAMINER = "EXM", "Examiner"
        OTHER = "OTH", "Other"

    class UavConfig(models.TextChoices):
        MULTIROTOR = "MULTI", "Multirotor"
        FIXED_WING = "FIXED", "Fixed-wing"
        HELICOPTER = "HELI", "Helicopter"
        VTOL = "VTOL", "VTOL / hybrid"
        OTHER = "OTHER", "Other"

    class EasaClass(models.TextChoices):
        C0 = "C0", "C0 (<250g)"
        C1 = "C1", "C1 (<900g)"
        C2 = "C2", "C2 (<4kg)"
        C3 = "C3", "C3 (<25kg)"
        C4 = "C4", "C4 (<25kg, no automation)"
        C5 = "C5", "C5 (STS-01)"
        C6 = "C6", "C6 (STS-02)"

    class MissionType(models.TextChoices):
        MAP = "MAP", "Mapping / Survey"
        INSP = "INSP", "Inspection"
        SAR = "SAR", "Search & Rescue"
        TRN = "TRN", "Training flight"
        REC = "REC", "Recreational"
        ISR = "ISR", "ISR / Surveillance"
        CRG = "CRG", "Cargo / logistics"
        EXP_MISSION = "EXP", "Experimental mission"

    class GcsFormFactor(models.TextChoices):
        HANDHELD = "HANDHELD", "Handheld controller"
        TABLET = "TABLET", "Tablet controller"
        RUGGED = "RUGGED", "Rugged tablet GCS"
        LAPTOP = "LAPTOP", "Laptop GCS"
        BRIEFCASE = "BRIEFCASE", "Portable briefcase GCS"
        VEHICLE = "VEHICLE", "Vehicle-mounted GCS"
        FIXED = "FIXED", "Fixed installation GCS"
        FPV = "FPV", "FPV controller + goggles"
        OTHER = "OTHER", "Other"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uas_flights",
    )

    # ---- Flight identification ----
    date = models.DateField()
    departure = models.CharField("Departure location", max_length=100)
    arrival = models.CharField("Arrival location", max_length=100)

    # Only required times: departure & arrival (off/on block)
    off_block = models.TimeField("Departure time", blank=True, null=True)
    on_block = models.TimeField("Arrival time", blank=True, null=True)

    # ---- Aircraft / GCS ----
    uav_type = models.CharField(
        "UAV configuration",
        max_length=10,
        choices=UavConfig.choices,
        help_text="Multirotor / fixed-wing / VTOL / heli, etc.",
    )
    uav_model = models.CharField(
        "UAV model",
        max_length=100,
        blank=True,
        help_text="e.g. fixed-wing piston trainer, Mavic 3 Pro",
    )
    uav_reg = models.CharField(
        "UAV registration",
        max_length=50,
        help_text="Aircraft registration / ID",
    )

    gcs_type = models.CharField(
        "GCS form factor",
        max_length=15,
        choices=GcsFormFactor.choices,
        blank=True,
        help_text="Handheld, laptop GCS, vehicle, etc.",
    )
    gcs_reg = models.CharField(
        "GCS registration / ID",
        max_length=50,
        blank=True,
    )

    # ---- Advanced classification (optional) ----
    uav_easa_class = models.CharField(
        "EASA class",
        max_length=3,
        choices=EasaClass.choices,
        blank=True,
    )
    mission_type = models.CharField(
        "Mission type",
        max_length=4,
        choices=MissionType.choices,
        blank=True,
    )
    gcs_software = models.CharField(
        "GCS software",
        max_length=50,
        blank=True,
        help_text="e.g. Embention, DJI Fly, QGroundControl…",
    )

    # ---- Pilot function for this flight ----
    pilot_role = models.CharField(
        "Pilot role",
        max_length=3,
        choices=PilotRole.choices,
        default=PilotRole.PIC,
    )

    # ---- Takeoffs / landings (day/night) ----
    takeoff_day = models.PositiveIntegerField("Takeoffs (day)", default=0)
    takeoff_night = models.PositiveIntegerField("Takeoffs (night)", default=0)
    landing_day = models.PositiveIntegerField("Landings (day)", default=0)
    landing_night = models.PositiveIntegerField("Landings (night)", default=0)

    # ---- Flight time in minutes, auto from dep/arr ----
    flight_time = models.PositiveIntegerField(
        "Flight time (min)", blank=True, null=True, editable=False
    )

    # ---- Simulator / training device ----
    is_simulator = models.BooleanField(
        "Simulator session",
        default=False,
    )
    simulator_type = models.CharField("Simulator type", max_length=100, blank=True)
    simulator_time = models.PositiveIntegerField(
        "Simulator time (min)", blank=True, null=True
    )

    # ---- Remarks ----
    remarks = models.TextField(
        "Remarks / skill tests / checks",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.date} {self.uav_type} {self.uav_reg} ({self.user})"

    # ---- Helpers for time calculations ----
    def _combine(self, t):
        if not t or not self.date:
            return None
        return datetime.combine(self.date, t)

    def save(self, *args, **kwargs):
        """
        Auto-calc flight time from departure & arrival
        (off_block / on_block) in minutes.
        """
        start = self._combine(self.off_block)
        end = self._combine(self.on_block)

        if start and end and end > start:
            delta = end - start
            self.flight_time = int(delta.total_seconds() // 60)
        else:
            self.flight_time = None

        super().save(*args, **kwargs)
