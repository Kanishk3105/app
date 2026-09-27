from django.contrib import admin

from apps.mappings.models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "assigned_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("patient__name", "doctor__name")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("patient", "doctor", "assigned_by")
