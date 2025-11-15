# Changelog

All notable changes to **UAS Logbook** will be documented in this file.

The format is:
- Version numbers: `vMAJOR.MINOR.PATCH`
- Dates in `YYYY-MM-DD`
- Categories: `Added`, `Changed`, `Fixed`, `Removed`

---

## [Unreleased]

- Planned: data integrity & audit trail (soft delete, change history)
- Planned: pilot confirmation & certifier approval workflow
- Planned: finer-grained roles for company / training org use

---

## [v0.3.0] – 2025-11-15

**Status:** current working version (local dev)

### Added
- **Audit view** (`/audit/`):
  - Read-only page intended for inspections/audits.
  - Compact pilot “card” with:
    - Small profile avatar
    - Pilot name and username
    - Status of medical certificate, flight crew licence, and other document (with “On file” / “Missing” pills).
  - Summary section:
    - Total filtered flight time
    - Total day/night takeoffs and landings
    - Last 90 days total flight time
  - Flights table:
    - Date, route, UAV, role, departure/arrival times, flight time, day/night TO & LDG.
  - **Print / Save as PDF** button for generating a paper/PDF copy.
  - CSV export button directly from the audit page.
  - **QR code** generated client-side (using QRious) encoding the current audit URL to quickly open the same view on another device (useful in checks / inspections).

- **Header user menu**:
  - Small avatar (24×24) next to username in the top bar.
  - Dropdown menu with:
    - Profile & documents
    - Settings (stub for now)
    - Audit view
    - Log out (via POST, CSRF-protected).

### Changed
- UI polish:
  - Unified dark theme with card-based layout (flights, filters, profile, audit).
  - Reduced avatar size in header to avoid dominating the layout.
  - Profile and documents page redesigned:
    - Two-column layout: compact pilot card + documents & preferences.
    - Clear “Profile photo / Medical certificate / Flight crew licence / Other document / Time display unit” fields.
    - Cleaner contrast (no more hard-to-read blue-on-blue).
  - Flights list page:
    - Modern layout with summary card, filters card, and flight table.
    - Better spacing, typography and hover states.
  - Audit view layout:
    - Structured into “Pilot card”, “Filters”, “Summary”, “Flights” sections.
    - Photo right-sized for an inspection screen, not full-page.

### Fixed
- Logout now uses a POST form instead of GET to match Django’s `LogoutView` defaults and avoid `405 Method Not Allowed`.

---

## [v0.2.0] – 2025-11-13

> First “real” iteration of the app as a usable UAS personal logbook.

### Added
- **Flight log model** (`FlightLogEntry`):
  - Per-user entries with:
    - Date
    - UAV type/config + model name
    - UAV registration (simple text)
    - GCS name/identifier
    - Pilot role (PIC, co-pilot, observer, student, instructor, examiner, other)
    - Departure and arrival aerodromes/locations
    - Operational times:
      - Off-block / On-block
      - Engine start / Engine stop
      - GCS connect / disconnect
      - Takeoff / Landing
    - Calculated durations (in minutes):
      - Flight time (based on takeoff–landing or block times)
      - Block time (on-block – off-block)
      - Engine time (engine stop – engine start)
      - GCS time (disconnect – connect)
    - Day/night landings and takeoffs
    - Simulator fields (basic support)
    - Free-text remarks.

- **Flight CRUD views**:
  - Flight list page showing user’s flights in a table.
  - Create/edit form for flights using `FlightLogEntryForm`.
  - Delete view for removing entries.
  - Basic authentication: only logged-in users can view/edit flights.

- **CSV export/import**:
  - Export current user’s flights to CSV (for backup or transfer).
  - Import from CSV with mapping to the current model fields (for migrating existing logbook data).

- **Templates**:
  - Basic `base.html` layout.
  - Initial `flight_list.html` and `flight_form.html` (minimal styling but functional).

---

## [v0.1.0] – 2025-11-13

> Initial project setup and bare-bones logbook.

### Added
- Django project **`config`**.
- Django app **`logbook`**.
- Basic settings:
  - SQLite database
  - `logbook` added to `INSTALLED_APPS`
  - Template directory at `templates/`
- Basic URLs:
  - Root URL leading to a simple flight list/home (later evolved).
  - Django admin enabled at `/admin/`.
- Initial `FlightLogEntry` model draft and admin registration so entries can be inspected from Django admin.
- Basic login/logout templates using Django’s built-in auth views.

---

Links and tags (when using git):

- `v0.1.0` – initial setup
- `v0.2.0` – first full logbook + CSV + basic UI
- `v0.3.0` – profile/docs + header avatar + audit view
