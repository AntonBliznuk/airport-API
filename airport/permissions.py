from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminUserOrReadOnly(BasePermission):
    """Allows read-only access for any user,
    but write permissions are only granted to admin users.
    """

    def has_permission(self, request, view):
        return True if request.method in SAFE_METHODS else request.user.is_staff