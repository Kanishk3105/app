from django.contrib import admin

from apps.doctors.models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialization", "email", "is_available", "created_at")
    list_filter = ("specialization", "is_available")
    search_fields = ("name", "email", "specialization")
    readonly_fields = ("created_at", "updated_at")
    raw_id_fields = ("created_by",)
