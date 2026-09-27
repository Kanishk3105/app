"""Fallback JSON responses for unmatched routes and server errors."""
from django.http import HttpResponseServerError, JsonResponse
from rest_framework import status


def _wants_json(request):
    return request.path.startswith("/api/") or "application/json" in request.headers.get(
        "Accept", ""
    )


def api_not_found(request, *args, **kwargs):
    """Return a JSON 404 for any unmatched path under ``/api/``."""
    return JsonResponse({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


def api_404_handler(request, exception=None):
    """``handler404`` - JSON for API/browser-JSON requests, simple page otherwise."""
    if _wants_json(request):
        return JsonResponse({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
    return JsonResponse({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)


def api_500_handler(request):
    """``handler500`` - never leak a stack trace to the client."""
    if _wants_json(request):
        return JsonResponse(
            {"detail": "A server error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    return HttpResponseServerError("A server error occurred.")
