from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj

class IsSelfProfile(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            return request.user.profile == obj
        except:
            return False

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS