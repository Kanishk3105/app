"""URL configuration for the healthcare backend API."""
from django.contrib import admin
from django.urls import include, path, re_path

from config.errors import api_404_handler, api_500_handler, api_not_found
from config.views import api_index

urlpatterns = [
    path("", api_index, name="api-index"),
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.patients.urls")),
    path("api/", include("apps.doctors.urls")),
    path("api/", include("apps.mappings.urls")),
    # Any unmatched /api/... path must answer with JSON, not an HTML 404 page.
    re_path(r"^api/", api_not_found),
]

handler404 = api_404_handler
handler500 = api_500_handler
