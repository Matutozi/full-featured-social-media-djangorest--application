from rest_framework.permissions import BasePermission


class IsAdminorStaff(BasePermission):
    """Class that manages permission for staff anf admin persons"""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_staff
        )
