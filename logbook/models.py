from django.db import models
from django.conf import settings
from datetime import datetime
from django.utils import timezone


class PilotProfile(models.Model):
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

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uas_flights",
    )

    # ---- Flight identification ----
    date = models.DateField()

    departure = models.CharField("Departure location", max_length=100)
    arrival = models.CharField("Arrival location", max_length=100)

    # Block times (used as "place and time of dep/arr")
    off_block = models.TimeField("Off block (departure time)", blank=True, null=True)
    on_block = models.TimeField("On block (arrival time)", blank=True, null=True)

    # ---- Aircraft / GCS ----
    uav_type = models.CharField(
        "UAV type (make/model/variant)",
        max_length=100,
        help_text="e.g. DJI Mavic 3, WingtraOne, etc.",
    )
    uav_reg = models.CharField(
        "UAV registration",
        max_length=50,
        help_text="Aircraft registration / ID",
    )

    gcs_type = models.CharField(
        "GCS type",
        max_length=100,
        blank=True,
        help_text="Ground control station make/model (optional)",
    )
    gcs_reg = models.CharField(
        "GCS registration / ID",
        max_length=50,
        blank=True,
    )

    engine_class = models.CharField(
        "Engine class (SE/ME)",
        max_length=10,
        blank=True,
        help_text="Optional for UAS, e.g. SE/ME or empty.",
    )

    # ---- Pilot function for this flight ----
    pilot_role = models.CharField(
        "Pilot role",
        max_length=3,
        choices=PilotRole.choices,
        default=PilotRole.PIC,
        help_text="Your function on this flight (PIC, observer, instructor, etc.)",
    )

    # ---- Operational times ----
    connection_time = models.TimeField(
        "GCS connected",
        blank=True,
        null=True,
        help_text="Time when GCS connected to UAV",
    )
    engine_start = models.TimeField("Engine start", blank=True, null=True)
    takeoff = models.TimeField("Takeoff", blank=True, null=True)
    landing = models.TimeField("Landing", blank=True, null=True)
    engine_stop = models.TimeField("Engine stop", blank=True, null=True)
    disconnection_time = models.TimeField(
        "GCS disconnected",
        blank=True,
        null=True,
        help_text="Time when GCS disconnected from UAV",
    )

    # ---- Takeoffs / landings (day/night) ----
    takeoff_day = models.PositiveIntegerField("Takeoffs (day)", default=0)
    takeoff_night = models.PositiveIntegerField("Takeoffs (night)", default=0)
    landing_day = models.PositiveIntegerField("Landings (day)", default=0)
    landing_night = models.PositiveIntegerField("Landings (night)", default=0)

    # ---- Durations in minutes (auto-calculated, not edited by hand) ----
    flight_time = models.PositiveIntegerField(
        "Flight time (min)", blank=True, null=True, editable=False
    )
    block_time = models.PositiveIntegerField(
        "Block time (min)", blank=True, null=True, editable=False
    )
    engine_time = models.PositiveIntegerField(
        "Engine time (min)", blank=True, null=True, editable=False
    )
    gcs_time = models.PositiveIntegerField(
        "GCS time (min)", blank=True, null=True, editable=False
    )

    # ---- Simulator / training device ----
    is_simulator = models.BooleanField(
        "Simulator session",
        default=False,
        help_text="Tick if this was an FSTD/simulator session rather than an actual flight.",
    )
    simulator_type = models.CharField("Simulator type", max_length=100, blank=True)
    simulator_time = models.PositiveIntegerField(
        "Simulator time (min)", blank=True, null=True
    )

    # ---- Remarks ----
    remarks = models.TextField(
        "Remarks / skill tests / checks",
        blank=True,
        help_text="Skill tests, proficiency checks, incidents, etc.",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.date} {self.uav_type} {self.uav_reg} ({self.user})"

    def _combine(self, t):
        if not t:
            return None
        return datetime.combine(self.date, t)

    def save(self, *args, **kwargs):
        """Auto-calc durations based purely on times."""
        def minutes_between(start, end):
            if start and end and end > start:
                delta = end - start
                return int(delta.total_seconds() // 60)
            return None

        t_takeoff = self._combine(self.takeoff)
        t_landing = self._combine(self.landing)
        t_off_block = self._combine(self.off_block)
        t_on_block = self._combine(self.on_block)
        t_eng_start = self._combine(self.engine_start)
        t_eng_stop = self._combine(self.engine_stop)
        t_conn = self._combine(self.connection_time)
        t_disc = self._combine(self.disconnection_time)

        # Always compute from times (they are not user-editable)
        self.flight_time = minutes_between(t_takeoff, t_landing)
        self.block_time = minutes_between(t_off_block, t_on_block)
        self.engine_time = minutes_between(t_eng_start, t_eng_stop)
        self.gcs_time = minutes_between(t_conn, t_disc)

        super().save(*args, **kwargs)
