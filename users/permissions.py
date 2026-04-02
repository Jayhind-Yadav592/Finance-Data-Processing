from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Sirf Admin users ko allow karta hai."""
    message = 'Only admin users can perform this action.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAnalystOrAdmin(BasePermission):
    """Analyst aur Admin dono ko allow karta hai."""
    message = 'Only analyst or admin users can perform this action.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_analyst)


class IsActiveUser(BasePermission):
    """Inactive users ko block karta hai."""
    message = 'Your account is inactive. Contact admin.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)