from django.urls import path

from apps.mappings.views import MappingListCreateView, MappingPatientDoctorsView

app_name = "mappings"

urlpatterns = [
    path("mappings/", MappingListCreateView.as_view(), name="mapping-list"),
    path("mappings/<int:pk>/", MappingPatientDoctorsView.as_view(), name="mapping-detail"),
]
