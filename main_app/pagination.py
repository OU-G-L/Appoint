from rest_framework.pagination import CursorPagination


class AppointmentsCPagination(CursorPagination):
    """
    Cursor-based pagination class for listing appointment records.

    - Paginates results using a cursor instead of offset-based pagination.
    - Orders appointments by 'time' field in ascending order.
    - Returns 5 appointments per page.
    """
    page_size = 5  # Number of appointments per page
    ordering = 'time'  # Sort appointments by time (ascending)
