from django.urls import path
from .views import *

app_name = "restaurant"

urlpatterns = [
    path('', ListRestaurants.as_view(), name='listRestaurant'),
    path('product/', ListCreateProducts.as_view(), name='listCreateProduct'),
    path('product/bulkdelete/', BulkDeleteProducts.as_view(), name='bulkdelete'),
    path('product/bulkavailable/', BulkAvailableProducts.as_view(), name='bulkavailable'),
    path('product/bulkunavailable/', BulkUnavailableProducts.as_view(), name='bulkunavailable'),
    path('product/<int:pk>/', RetrieveUpdateProduct.as_view(), name='retrieveUpdateProduct'),
    path('deliverycharge/', GetDeliveryCharge.as_view(), name='getDeliveryCharge'),
    path('search/', Search.as_view(), name='search'),
]