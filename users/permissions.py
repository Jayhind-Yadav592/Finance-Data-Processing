from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    
    message = 'Only admin users can perform this action.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsAnalystOrAdmin(BasePermission):
   
    message = 'Only analyst or admin users can perform this action.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_analyst)


class IsActiveUser(BasePermission):
    
    message = 'Your account is inactive. Contact admin.'

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_active)