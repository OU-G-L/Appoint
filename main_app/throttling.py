from rest_framework.throttling import UserRateThrottle


class ReserveAppointmentThrottle(UserRateThrottle):
    """
    Custom throttle class to limit the rate of appointment reservation requests by authenticated users.
    The rate limit should be configured in settings.py under the 'reserve-appointment' scope.
    """
    scope = 'reserve-appointment'


class AppointmentCreateThrottle(UserRateThrottle):
    """
    Custom throttle class to limit the rate of appointment creation requests by authenticated users.
    The rate limit should be configured in settings.py under the 'appointment-create' scope.
    """
    scope = 'appointment-create'
