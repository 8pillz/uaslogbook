from datetime import timedelta
import csv

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import FlightLogEntry, PilotProfile
from .forms import FlightLogEntryForm, PilotProfileForm


@login_required
def flight_list(request):
    flights = FlightLogEntry.objects.all().order_by("-date")

    # --- Filters via query params ---
    start = request.GET.get("start")  # YYYY-MM-DD
    end = request.GET.get("end")
    uav_query = request.GET.get("uav")
    role = request.GET.get("role")

    if start:
        flights = flights.filter(date__gte=start)
    if end:
        flights = flights.filter(date__lte=end)
    if uav_query:
        flights = flights.filter(uav_type__icontains=uav_query)
    if role:
        flights = flights.filter(pilot_role=role)

    # Totals for filtered flights
    totals = flights.aggregate(
        total_flight=Sum("flight_time"),
        total_block=Sum("block_time"),
        total_engine=Sum("engine_time"),
        total_gcs=Sum("gcs_time"),
    )

    # --- Stats (all-time / last 30 days on full dataset) ---
    today = timezone.now().date()
    last_30 = today - timedelta(days=30)

    recent_qs = FlightLogEntry.objects.filter(date__gte=last_30)
    recent_time = recent_qs.aggregate(Sum("flight_time")).get("flight_time__sum") or 0

    most_flown_qs = (
        FlightLogEntry.objects
        .values("uav_type")
        .annotate(total_time=Sum("flight_time"))
        .order_by("-total_time")
    )
    if most_flown_qs:
        most_flown = most_flown_qs[0]
        most_flown_uav = most_flown["uav_type"]
        most_flown_uav_time = most_flown["total_time"] or 0
    else:
        most_flown_uav = None
        most_flown_uav_time = 0

    stats = {
        "total_flights": FlightLogEntry.objects.count(),
        "recent_flights": recent_qs.count(),
        "recent_flight_time": recent_time,
        "most_flown_uav": most_flown_uav,
        "most_flown_uav_time": most_flown_uav_time,
    }

    # For role filter dropdown
    roles = FlightLogEntry.PilotRole.choices

    context = {
        "flights": flights,
        "totals": totals,
        "stats": stats,
        "roles": roles,
        "filters": {
            "start": start or "",
            "end": end or "",
            "uav": uav_query or "",
            "role": role or "",
        },
    }
    return render(request, "logbook/flight_list.html", context)


@login_required
def flight_create(request):
    if request.method == "POST":
        form = FlightLogEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user  # still safe even if it's only you
            entry.save()
            return redirect("flight_list")
    else:
        form = FlightLogEntryForm()

    return render(request, "logbook/flight_form.html", {"form": form})


@login_required
def flight_edit(request, pk):
    entry = get_object_or_404(FlightLogEntry, pk=pk)

    if request.method == "POST":
        form = FlightLogEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect("flight_list")
    else:
        form = FlightLogEntryForm(instance=entry)

    return render(request, "logbook/flight_form.html", {"form": form})


@login_required
def flight_delete(request, pk):
    entry = get_object_or_404(FlightLogEntry, pk=pk)
    if request.method == "POST":
        entry.delete()
        return redirect("flight_list")
    return render(request, "logbook/flight_confirm_delete.html", {"flight": entry})


@login_required
def flight_export_csv(request):
    flights = FlightLogEntry.objects.all().order_by("date")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename=\"uas_logbook.csv\"'

    writer = csv.writer(response)

    # Header row – aligned with current model
    writer.writerow([
        "Date",
        "Departure",
        "Arrival",
        "Off block",
        "On block",
        "UAV type",
        "UAV registration",
        "GCS type",
        "GCS registration",
        "Engine class (SE/ME)",
        "Pilot role",
        "GCS connected",
        "Engine start",
        "Takeoff",
        "Landing",
        "Engine stop",
        "GCS disconnected",
        "Takeoffs (day)",
        "Takeoffs (night)",
        "Landings (day)",
        "Landings (night)",
        "Flight time (min)",
        "Block time (min)",
        "Engine time (min)",
        "GCS time (min)",
        "Simulator?",
        "Simulator type",
        "Simulator time (min)",
        "Remarks",
    ])

    for f in flights:
        writer.writerow([
            f.date,
            f.departure,
            f.arrival,
            f.off_block,
            f.on_block,
            f.uav_type,
            f.uav_reg,
            f.gcs_type,
            f.gcs_reg,
            f.engine_class,
            f.get_pilot_role_display(),
            f.connection_time,
            f.engine_start,
            f.takeoff,
            f.landing,
            f.engine_stop,
            f.disconnection_time,
            f.takeoff_day,
            f.takeoff_night,
            f.landing_day,
            f.landing_night,
            f.flight_time,
            f.block_time,
            f.engine_time,
            f.gcs_time,
            "Yes" if f.is_simulator else "No",
            f.simulator_type,
            f.simulator_time,
            f.remarks,
        ])

    return response


@login_required
def profile_view(request):
    profile, _ = PilotProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = PilotProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = PilotProfileForm(instance=profile)

    context = {
        "profile": profile,
        "form": form,
    }
    return render(request, "profile.html", context)
