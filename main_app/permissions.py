from rest_framework import permissions


class IsScheduler(permissions.BasePermission):
    """
    Custom permission to allow access only to users with the 'scheduler' role.
    """
    def has_permission(self, request, view):
        # Check if user has a role_profile and the role is 'scheduler'
        return hasattr(request.user, 'role_profile') and request.user.role_profile.role == 'scheduler'


class IsBooker(permissions.BasePermission):
    """
    Custom permission to allow access only to users with the 'booker' role.
    """
    def has_permission(self, request, view):
        # Check if user has a role_profile and the role is 'booker'
        return hasattr(request.user, 'role_profile') and request.user.role_profile.role == 'booker'
