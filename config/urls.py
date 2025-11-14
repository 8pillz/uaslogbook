from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from logbook import views as logbook_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # Logbook
    path("", logbook_views.flight_list, name="home"),
    path("flights/", logbook_views.flight_list, name="flight_list"),
    path("flights/new/", logbook_views.flight_create, name="flight_create"),
    path("flights/<int:pk>/edit/", logbook_views.flight_edit, name="flight_edit"),
    path("flights/<int:pk>/delete/", logbook_views.flight_delete, name="flight_delete"),
    path("flights/export/", logbook_views.flight_export_csv, name="flight_export_csv"),

    # Profile
    path("profile/", logbook_views.profile_view, name="profile"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
