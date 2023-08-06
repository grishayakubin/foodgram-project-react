from rest_framework.permissions import (BasePermission,
                                        IsAuthenticatedOrReadOnly)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in ('GET',)
            or request.user.is_authenticated
            and request.user.is_admin
        )


class IsOwnerUserOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (request.user == obj)
            or request.user.is_admin
        )


class IsAuthorStaffOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (request.user == obj.author)
            or request.user.is_staff
        )
