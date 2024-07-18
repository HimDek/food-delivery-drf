from django.urls import path
from .views import *

app_name = "order"

urlpatterns = [
    path('', CreateOrder.as_view(), name='createOrder'),
    path('pending/', ListPendingOrder.as_view(), name='listPendingOrder'),
    path('past/', ListPastOrder.as_view(), name='listPastOrder'),
    path('<int:pk>/', RetrieveOrder.as_view(), name='retrieveOrder'),
    path('cancel/', CancelOrder.as_view(), name='cancelOrder'),
    path('accept/', AcceptOrder.as_view(), name='accept'),
    path('cookingfinished/', OrderCookingFinished.as_view(), name='cookingFinished'),
    path('pickedup/', OrderPickedUp.as_view(), name='pickedUp'),
    path('arrived/', OrderArrived.as_view(), name='arrived'),
    path('delivered/', OrderDelivered.as_view(), name='delivered'),
    path('paidtorestaurant/', OrderPaidToRestaurant.as_view(), name='paidToRestaurant'),
    path('paidtorestaurantconfirm/', OrderPaidToRestaurantConfirm.as_view(), name='paidToRestaurantConfirm'),
    path('availableDeliveryMan/', ListAvailableDeliveryMan.as_view(), name='listAvailableDeliveryMan'),
]