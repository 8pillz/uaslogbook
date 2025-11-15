from django.contrib import admin
from django.urls import path
from logbook import views as logbook_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # HOME → flight list
    path("", logbook_views.flight_list, name="home"),

    path("flights/", logbook_views.flight_list, name="flight_list"),
    path("flights/new/", logbook_views.flight_create, name="flight_create"),
    path("flights/<int:pk>/edit/", logbook_views.flight_edit, name="flight_edit"),
    path("flights/<int:pk>/delete/", logbook_views.flight_delete, name="flight_delete"),
    path("flights/export/", logbook_views.flight_export_csv, name="flight_export_csv"),
    path("flights/import/", logbook_views.flight_import_csv, name="flight_import"),

    path("profile/", logbook_views.profile_view, name="profile"),
    path("settings/", logbook_views.settings_view, name="settings"),
    path("audit/", logbook_views.audit_view, name="audit"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
