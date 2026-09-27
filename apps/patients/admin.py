from django.contrib import admin

from apps.patients.models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "age", "gender", "created_by", "created_at")
    list_filter = ("gender", "created_at")
    search_fields = ("name", "email", "created_by__email")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("created_by",)
