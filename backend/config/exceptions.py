"""
Project-wide DRF exception handler.

Two gaps in DRF's default exception handling caused unhandled 500 errors:

1. Model-level validation. Task.save() calls full_clean(), which raises
   django.core.exceptions.ValidationError - a *Django* exception, not the
   rest_framework.exceptions.ValidationError DRF's default handler knows
   how to turn into a 400 response. Any save() that trips clean() (e.g.
   assigning a task to an employee outside the task's department) crashed
   with a 500 instead of returning a normal validation error.

2. Deleting a row that's still referenced by a PROTECT foreign key raises
   django.db.models.ProtectedError, which also isn't a DRF exception, so
   it also fell through to a 500 (e.g. deleting a Department that still
   has employees or tasks).

This handler converts both into ordinary 400 responses, in the same shape
the frontend already has to handle for regular serializer validation
errors, so callers don't need special-case handling for these paths.
"""

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler


def _django_validation_error_to_drf(exc):
    if hasattr(exc, "message_dict"):
        detail = exc.message_dict
    elif hasattr(exc, "messages"):
        detail = exc.messages
    else:
        detail = str(exc)
    return DRFValidationError(detail)


def custom_exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = _django_validation_error_to_drf(exc)

    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, ProtectedError):
        return Response(
            {
                "detail": (
                    "This item can't be deleted because other records "
                    "still depend on it."
                )
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Anything else falls through to Django's normal 500 handling.
    return None