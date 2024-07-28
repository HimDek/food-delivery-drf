from rest_framework.permissions import (
    BasePermission,
    SAFE_METHODS,
)


class IsInProfileMenuOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return (
                obj.restaurant == request.user.profile or request.method in SAFE_METHODS
            )
        except:
            return request.method in SAFE_METHODS
