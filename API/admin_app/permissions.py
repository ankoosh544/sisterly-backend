from rest_framework.permissions import BasePermission


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return (request.user.is_admin or request.user.is_superuser) and request.user.is_active
        return False
