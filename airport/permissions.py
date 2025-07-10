from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminUserOrReadOnly(BasePermission):
    """Allows read-only access for any user,
    but write permissions are only granted to admin users.
    """

    def has_permission(self, request, view):
        return True if request.method in SAFE_METHODS else request.user.is_staff


class IsOwnerOrIsAdminOrReadOnly(BasePermission):
    """Custom permission:
    - Only allow access if the user is admin or the owner of the object.
    - Deny all access (read or write) to other users or anonymous users.
    """

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_staff:
            return True

        return obj.user == request.user


class IsOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user
