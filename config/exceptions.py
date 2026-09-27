"""Custom DRF exception handling so every API error returns clean JSON."""
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.http import Http404
from rest_framework import exceptions
from rest_framework.views import exception_handler


def api_exception_handler(exc, context):
    """Normalize error payloads produced by DRF.

    The result is always a JSON object::

        {"detail": "..."}             # non-field errors (401/403/404/500)
        {"<field>": ["..."], ...}     # field validation errors (400)
    """
    if isinstance(exc, Http404):
        exc = exceptions.NotFound()
    elif isinstance(exc, DjangoPermissionDenied):
        exc = exceptions.PermissionDenied()

    return exception_handler(exc, context)
