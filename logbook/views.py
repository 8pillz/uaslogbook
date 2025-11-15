from datetime import timedelta
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .forms import FlightLogEntryForm, PilotProfileForm, PilotSettingsForm
from .models import FlightLogEntry, PilotProfile
from .forms import FlightLogEntryForm, PilotProfileForm, PilotSettingsForm 

@login_required
def audit_view(request):
    """
    Compact, read-only view to show pilot documents and flights
    in a way that is easy to show to an auditor.
    """
    profile, _ = PilotProfile.objects.get_or_create(user=request.user)

    start = request.GET.get("start")
    end = request.GET.get("end")

    flights = FlightLogEntry.objects.filter(user=request.user).order_by("-date")

    if start:
        flights = flights.filter(date__gte=start)
    if end:
        flights = flights.filter(date__lte=end)

    totals = flights.aggregate(
        total_flight=Sum("flight_time"),
        total_takeoff_day=Sum("takeoff_day"),
        total_takeoff_night=Sum("takeoff_night"),
        total_landing_day=Sum("landing_day"),
        total_landing_night=Sum("landing_night"),
    )

    today = timezone.now().date()
    last_90 = today - timezone.timedelta(days=90)
    recent = FlightLogEntry.objects.filter(user=request.user, date__gte=last_90)
    recent_time = recent.aggregate(Sum("flight_time"))["flight_time__sum"] or 0

    context = {
        "profile": profile,
        "flights": flights,
        "totals": totals,
        "recent_90_days_time": recent_time,
        "filters": {
            "start": start or "",
            "end": end or "",
        },
    }
    return render(request, "audit.html", context)


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
    )

    # --- Stats (all-time / last 30 days on full dataset) ---
    today = timezone.now().date()
    last_30 = today - timedelta(days=30)

    recent_qs = FlightLogEntry.objects.filter(date__gte=last_30)
    recent_time = recent_qs.aggregate(Sum("flight_time")).get("flight_time__sum") or 0

    # most flown UAV by total flight_time
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

    total_takeoffs = FlightLogEntry.objects.aggregate(
        total=Sum("takeoff_day") + Sum("takeoff_night")
    )["total"] or 0
    total_landings = FlightLogEntry.objects.aggregate(
        total=Sum("landing_day") + Sum("landing_night")
    )["total"] or 0

    stats = {
        "total_flights": FlightLogEntry.objects.count(),
        "recent_flights": recent_qs.count(),
        "recent_flight_time": recent_time,
        "most_flown_uav": most_flown_uav,
        "most_flown_uav_time": most_flown_uav_time,
        "total_takeoffs": total_takeoffs,
        "total_landings": total_landings,
    }

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
def flight_import_csv(request):
    """
    Import flights from a CSV file.
    Expected columns (same as export, but you can start minimal):
    Date, Departure, Arrival, Departure time, Arrival time,
    UAV configuration, UAV model, UAV registration,
    GCS form factor, GCS registration,
    EASA class, Mission type, GCS software,
    Takeoffs (day), Takeoffs (night), Landings (day), Landings (night),
    Flight time (min), Simulator?, Simulator type, Simulator time (min), Remarks
    """
    if request.method == "POST" and request.FILES.get("file"):
        f = request.FILES["file"]
        try:
            wrapper = TextIOWrapper(f.file, encoding="utf-8")
            reader = csv.DictReader(wrapper)
        except Exception:
            messages.error(request, "Could not read CSV file.")
            return redirect("flight_import")

        created = 0
        for row in reader:
            try:
                date_str = row.get("Date")
                dep = row.get("Departure") or ""
                arr = row.get("Arrival") or ""
                if not date_str or not dep or not arr:
                    continue  # skip bad lines

                from datetime import datetime
                date = datetime.strptime(date_str, "%Y-%m-%d").date()

                off_block = row.get("Departure time") or None
                on_block = row.get("Arrival time") or None

                def parse_time(val):
                    if not val:
                        return None
                    try:
                        return datetime.strptime(val.strip(), "%H:%M").time()
                    except ValueError:
                        return None

                ob_time = parse_time(off_block)
                on_time = parse_time(on_block)

                entry = FlightLogEntry(
                    user=request.user,
                    date=date,
                    departure=dep,
                    arrival=arr,
                    off_block=ob_time,
                    on_block=on_time,
                    uav_type=row.get("UAV configuration") or FlightLogEntry.UavConfig.OTHER,
                    uav_model=row.get("UAV model") or "",
                    uav_reg=row.get("UAV registration") or "",
                    gcs_type=row.get("GCS form factor") or "",
                    gcs_reg=row.get("GCS registration") or "",
                    uav_easa_class=row.get("EASA class") or "",
                    mission_type=row.get("Mission type") or "",
                    gcs_software=row.get("GCS software") or "",
                    takeoff_day=int(row.get("Takeoffs (day)") or 0),
                    takeoff_night=int(row.get("Takeoffs (night)") or 0),
                    landing_day=int(row.get("Landings (day)") or 0),
                    landing_night=int(row.get("Landings (night)") or 0),
                    is_simulator=(row.get("Simulator?") or "").strip().lower() == "yes",
                    simulator_type=row.get("Simulator type") or "",
                    simulator_time=int(row.get("Simulator time (min)") or 0),
                    remarks=row.get("Remarks") or "",
                )
                entry.save()
                created += 1
            except Exception:
                # You can log errors if you want per-row diagnostics
                continue

        messages.success(request, f"Imported {created} flights from CSV.")
        return redirect("flight_list")

    return render(request, "logbook/flight_import.html")

@login_required
def settings_view(request):
    profile, _ = PilotProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = PilotSettingsForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("settings")
    else:
        form = PilotSettingsForm(instance=profile)

    return render(request, "settings.html", {"form": form})

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
    response["Content-Disposition"] = 'attachment; filename="uas_logbook.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Date",
        "Departure",
        "Arrival",
        "Departure time",
        "Arrival time",
        "UAV type",
        "UAV registration",
        "GCS type",
        "GCS registration",
        "Pilot role",
        "Takeoffs (day)",
        "Takeoffs (night)",
        "Landings (day)",
        "Landings (night)",
        "Flight time (min)",
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
            f.get_uav_type_display(),
            f.uav_reg,
            f.get_gcs_type_display() if f.gcs_type else "",
            f.gcs_reg,
            f.get_pilot_role_display(),
            f.takeoff_day,
            f.takeoff_night,
            f.landing_day,
            f.landing_night,
            f.flight_time,
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
