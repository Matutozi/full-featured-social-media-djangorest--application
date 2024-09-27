from rest_framework.exceptions import ValidationError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        return Response(
            {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Validation error",
                "data": exc.detail,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if response is None:
        return Response(
            {
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": "An unexpected error occurred.",
                "data": str(exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return Response(
        {
            "status_code": response.status_code,
            "message": "An error occurred.",
            "data": response.data,
        },
        status=response.status_code,
    )
