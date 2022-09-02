from rest_framework.permissions import BasePermission

METHODS = ['GET', 'PUT']


class ProductPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in METHODS:
            return request.method == 'GET' or (request.user and request.user.is_authenticated)
        return False


# Da definire bene quando sarà implementato SPID
class SPIDPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user and request.user.is_authenticated:
            return True
        return False
