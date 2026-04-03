from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    DRF ka default exception handler extend karke
    consistent error format deta hai:
    {
        "error": "...",
        "details": {...}   (optional, validation errors ke liye)
    }
    """
    response = exception_handler(exc, context)

    if response is not None:
        error_data = {}

        if response.status_code == status.HTTP_400_BAD_REQUEST:
            error_data['error'] = 'Invalid input. Please check the fields below.'
            error_data['details'] = response.data

        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            error_data['error'] = 'Authentication required. Please login to continue.'

        elif response.status_code == status.HTTP_403_FORBIDDEN:
            detail = response.data.get('detail', '')
            error_data['error'] = str(detail) if detail else 'You do not have permission to perform this action.'

        elif response.status_code == status.HTTP_404_NOT_FOUND:
            error_data['error'] = 'The requested resource was not found.'

        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            error_data['error'] = f'Method not allowed on this endpoint.'

        else:
            error_data['error'] = 'An unexpected error occurred.'
            error_data['details'] = response.data

        response.data = error_data

    return response