from rest_framework.permissions import BasePermission, IsAuthenticated, IsAuthenticatedOrReadOnly, SAFE_METHODS

class IsDeliveryManUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.deliveryMan.user == request.user

class IsCustomerUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.customer.user == request.user

class IsRestaurantUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.restaurant.user == request.user