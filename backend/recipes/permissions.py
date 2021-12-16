from rest_framework import permissions


class IsAuthorOrAdminOrReadOnlyPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        is_method_safe = request.method in permissions.SAFE_METHODS
        return is_method_safe or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        is_method_safe = request.method in permissions.SAFE_METHODS
        is_author = obj.author == request.user
        is_admin = request.user.is_staff
        return is_method_safe or is_author or is_admin