from rest_framework.permissions import BasePermission, IsAuthenticated


class IsAdminorStaff(BasePermission):
    """Class that manages permission for staff anf admin persons"""

    message = "Ban or unban operation fails"

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_staff
        )
