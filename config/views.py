"""Root API index - a human-friendly JSON map of the API."""
from django.http import JsonResponse

ENDPOINTS = {
    "authentication": [
        {"method": "POST", "path": "/api/auth/register/", "auth": "public",
         "description": "Create a new user (name, email, password)."},
        {"method": "POST", "path": "/api/auth/login/", "auth": "public",
         "description": "Exchange credentials for JWT access + refresh tokens."},
        {"method": "POST", "path": "/api/auth/token/refresh/", "auth": "public",
         "description": "Rotate the access token using a refresh token."},
        {"method": "POST", "path": "/api/auth/logout/", "auth": "bearer",
         "description": "Confirm logout (client discards its tokens)."},
        {"method": "GET", "path": "/api/auth/me/", "auth": "bearer",
         "description": "Return the currently authenticated user."},
    ],
    "patients": [
        {"method": "POST", "path": "/api/patients/", "auth": "bearer",
         "description": "Create a patient owned by the request user."},
        {"method": "GET", "path": "/api/patients/", "auth": "bearer",
         "description": "List the request user's patients."},
        {"method": "GET", "path": "/api/patients/<id>/", "auth": "bearer",
         "description": "Retrieve one of the request user's patients."},
        {"method": "PUT", "path": "/api/patients/<id>/", "auth": "bearer",
         "description": "Replace a patient record."},
        {"method": "PATCH", "path": "/api/patients/<id>/", "auth": "bearer",
         "description": "Partially update a patient record."},
        {"method": "DELETE", "path": "/api/patients/<id>/", "auth": "bearer",
         "description": "Delete a patient record."},
    ],
    "doctors": [
        {"method": "POST", "path": "/api/doctors/", "auth": "bearer",
         "description": "Register a doctor."},
        {"method": "GET", "path": "/api/doctors/", "auth": "bearer",
         "description": "List all doctors."},
        {"method": "GET", "path": "/api/doctors/<id>/", "auth": "bearer",
         "description": "Retrieve a doctor."},
        {"method": "PUT", "path": "/api/doctors/<id>/", "auth": "bearer",
         "description": "Replace a doctor."},
        {"method": "PATCH", "path": "/api/doctors/<id>/", "auth": "bearer",
         "description": "Partially update a doctor."},
        {"method": "DELETE", "path": "/api/doctors/<id>/", "auth": "bearer",
         "description": "Delete a doctor."},
    ],
    "mappings": [
        {"method": "POST", "path": "/api/mappings/", "auth": "bearer",
         "description": "Assign a doctor to a patient."},
        {"method": "GET", "path": "/api/mappings/", "auth": "bearer",
         "description": "List the request user's patient-doctor mappings."},
        {"method": "GET", "path": "/api/mappings/<patient_id>/", "auth": "bearer",
         "description": "All doctors assigned to a patient."},
        {"method": "DELETE", "path": "/api/mappings/<id>/", "auth": "bearer",
         "description": "Remove a mapping."},
    ],
    "other": [
        {"method": "GET", "path": "/admin/", "auth": "session",
         "description": "Django admin site."},
    ],
}


def api_index(request):
    """GET / - JSON index of every endpoint (no authentication required)."""
    return JsonResponse(
        {
            "name": "Healthcare Backend API",
            "version": "1.0.0",
            "authentication": "Send `Authorization: Bearer <access_token>` on protected routes.",
            "how_to_get_a_token": "POST /api/auth/login/ -> {\"access\": ..., \"refresh\": ...}",
            "documentation": "See README.md and postman_collection.json in the project root.",
            "endpoints": ENDPOINTS,
        },
        status=200,
    )
