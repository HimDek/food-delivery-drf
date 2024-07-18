import requests
import math
from django.db.models import Q
from rest_framework import generics, views, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import *
from .serializers import *
from .permissions import *
from user.models import Profile
from user.serializers import *
from restaurant.models import Product, Variant


def getDeliveryMan(restaurantId):
    restaurant = Profile.objects.get(id=restaurantId)
    deliveryMan = Profile.objects_within_square(
        restaurant.latitude, restaurant.longitude, 20
    ).filter(kind="D")
    availableDeliveryMan = deliveryMan.filter(available=True)

    if len(availableDeliveryMan) > 0:
        nearestAvailableDeliveryMan = deliveryMan[0]
        for man in availableDeliveryMan:
            if calculate_distance(
                man.latitude, man.longitude, restaurant.latitude, restaurant.longitude
            ) < calculate_distance(
                nearestAvailableDeliveryMan.latitude,
                nearestAvailableDeliveryMan.longitude,
                restaurant.latitude,
                restaurant.longitude,
            ):
                nearestAvailableDeliveryMan = man
        return nearestAvailableDeliveryMan
    elif len(deliveryMan) > 0:
        nearestDeliveryMan = deliveryMan[0]
        for man in deliveryMan:
            if calculate_distance(
                man.latitude, man.longitude, restaurant.latitude, restaurant.longitude
            ) < calculate_distance(
                nearestDeliveryMan.latitude,
                nearestDeliveryMan.longitude,
                restaurant.latitude,
                restaurant.longitude,
            ):
                nearestDeliveryMan = man
        return nearestDeliveryMan
    else:
        return None


def getTravelDistanceDuration(latitude1, longitude1, latitude2, longitude2):
    url = f"http://dev.virtualearth.net/REST/v1/Routes?wayPoint.1={latitude1},{longitude1}&wayPoint.2={latitude2},{longitude2}&optimize=timeWithTraffic&travelMode=Driving&key=Avp1HW_M-FcjR-yGlkZxwSGjBoMpHZejnAB1XjcCqh23apgSMBoaaNJ3_CZDdqYy"
    response = requests.get(url).json()
    distance = 1000
    if len(response["resourceSets"]):
        if len(response["resourceSets"][0]["resources"]):
            distance = response["resourceSets"][0]["resources"][0]["travelDistance"]
            duration = response["resourceSets"][0]["resources"][0][
                "travelDurationTraffic"
            ]
    return (distance, duration)


def calculate_distance(lat1, lon1, lat2, lon2):
    # Function to calculate distance between two points using Haversine formula
    from math import radians, sin, cos, sqrt, atan2

    R = 6371.0  # approximate radius of Earth in km

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance


# Create your views here.


class ListPendingOrder(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["placedOn", "-placedOn", "lastUpdateOn", "-lastUpdateOn"]
    ordering = ["-placedOn"]

    def get_queryset(self):
        profile = self.request.user.profile
        if profile.kind == "C":
            return Order.objects.filter(
                Q(customer=profile)
                & (
                    Q(status="PL")
                    | Q(status="CK")
                    | Q(status="WT")
                    | Q(status="PU")
                    | Q(status="AR")
                )
            )
        else:
            return Order.objects.filter(
                (Q(restaurant=profile) | Q(deliveryMan=profile))
                & (
                    Q(paymentStatus="NP")
                    | Q(paymentStatus="RC")
                    | Q(paymentStatus="WT")
                )
            )


class ListPastOrder(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["placedOn", "-placedOn", "lastUpdateOn", "-lastUpdateOn"]
    ordering = ["-placedOn"]

    def get_queryset(self):
        profile = self.request.user.profile
        if profile.kind == "C":
            return Order.objects.filter(
                Q(customer=profile)
                & (Q(status="DL") | Q(status="XC") | Q(status="XR") | Q(status="XD"))
            )
        else:
            return Order.objects.filter(
                (Q(restaurant=profile) | Q(deliveryMan=profile))
                & (
                    Q(status="XC")
                    | Q(status="XR")
                    | Q(status="XD")
                    | Q(paymentStatus="CM")
                )
            )


class RetrieveOrder(generics.RetrieveAPIView):
    permission_classes = [IsCustomerUser | IsRestaurantUser | IsDeliveryManUser]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class ListAvailableDeliveryMan(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.filter(kind="D", available=True)


class CreateOrder(views.APIView):
    permission_classes = [IsCustomerUser]

    def post(self, request):
        profile = request.user.profile
        content = []
        productTotal = 0
        receivedContent = json.loads(request.POST.get("content"))
        restaurant = Product.objects.get(id=receivedContent[0]["product"]).restaurant

        travelDistanceDuration = getTravelDistanceDuration(
            restaurant.latitude,
            restaurant.longitude,
            request.POST.get("latitude"),
            request.POST.get("longitude"),
        )
        deliveryCharge = math.ceil(20 + (5 * travelDistanceDuration[0]))

        if travelDistanceDuration[0] > 20:
            error = {
                "detail": f"This restaurant is currently not delivering to the specified location"
            }
            return Response(error, status=400)

        for receivedEntry in receivedContent:
            if not Product.objects.filter(id=receivedEntry["product"]).exists():
                error = {
                    "detail": f'Invalid product data: productId={receivedEntry["product"]}'
                }
                return Response(error, status=400)
            else:
                product = Product.objects.get(id=receivedEntry["product"])
                if restaurant == product.restaurant:
                    content.append({})
                    content[-1]["variants"] = []
                    content[-1]["product"] = {}
                    content[-1]["product"]["name"] = product.name
                    content[-1]["product"]["description"] = product.description
                    for variant, quantity in receivedEntry["quantities"].items():
                        if int(quantity) > 0:
                            if Variant.objects.filter(
                                id=int(variant), product=receivedEntry["product"]
                            ).exists():
                                cost = Variant.objects.get(id=int(variant)).price
                                name = Variant.objects.get(id=int(variant)).name
                                price = quantity * cost
                                content[-1]["variants"].append(
                                    {
                                        "name": name,
                                        "cost": cost,
                                        "quantity": quantity,
                                        "price": price,
                                    }
                                )
                                productTotal += price
                    if len(content[-1]["variants"]) == 0:
                        content.pop()
                else:
                    error = {"detail": f"Products from different restaurant"}
                    return Response(error, status=400)

        deliveryMan = getDeliveryMan(restaurant.id)
        if deliveryMan == None:
            error = {"detail": f"No delivery Partner Available"}
            return Response(error, status=400)

        order = Order.objects.create(
            content=json.dumps(content),
            productTotal=productTotal,
            deliveryCharge=deliveryCharge,
            latitude=request.POST.get("latitude"),
            longitude=request.POST.get("longitude"),
            restaurant=restaurant,
            customer=profile,
            deliveryMan=deliveryMan,
        )
        data = {"open": "order", "id": f"{order.id}"}

        Notification.objects.create(
            profile=profile,
            title=f"Order #{order.id} Placed",
            body="Your Order was received by the restaurant",
            data=data,
        )
        Notification.objects.create(
            profile=restaurant,
            title=f"Order #{order.id} Received",
            body=f"You received an Order from {profile.user.first_name} {profile.user.last_name}",
            data=data,
        )
        Notification.objects.create(
            profile=deliveryMan,
            title=f"Delivery of Order #{self.id} Assigned",
            body=f"Delivery of order from {self.restaurant.restaurantName} to {self.customer.user.first_name} {self.customer.user.last_name} was assigned to you",
            data=data,
        )

        return Response(OrderSerializer(order).data)


class CancelOrder(views.APIView):
    permission_classes = [IsCustomerUser | IsRestaurantUser | IsDeliveryManUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        data = {"open": "order", "id": f"{order.id}"}
        profile = request.user.profile
        if profile == order.customer and order.status == "PL":
            order.status = "XC"
            order.cancelledReason = request.POST.get("reason")
            order.save()
            Notification.objects.create(
                profile=self.restaurant,
                title=f"Order #{self.id} Cancelled",
                body=f"{self.customer.user.first_name} {self.customer.user.last_name} cancelled their order",
                data=data,
            )
            Notification.objects.create(
                profile=self.deliveryMan,
                title=f"Order #{self.id} Cancelled",
                body=f"{self.customer.user.first_name} {self.customer.user.last_name} cancelled their order from {self.restaurant.restaurantName}",
                data=data,
            )
        elif profile == order.restaurant and order.status in ["PL", "CK", "WT"]:
            order.status = "XR"
            order.cancelledReason = request.POST.get("reason")
            order.save()
            Notification.objects.create(
                profile=self.customer,
                title=f"Order #{self.id} Cancelled",
                body=f"Your Order from {self.restaurant.restaurantName} was cancelled by the restaurant",
                data=data,
            )
            Notification.objects.create(
                profile=self.deliveryMan,
                title=f"Order #{self.id} Cancelled",
                body=f"Order #{self.id} from {self.restaurant.restaurantName} to {self.customer.user.first_name} {self.customer.user.last_name} was cancelled by the restaurant",
                data=data,
            )
        elif profile == order.deliveryMan and order.status in ["PL", "PU", "AR"]:
            order.status = "XD"
            order.cancelledReason = request.POST.get("reason")
            order.save()
            Notification.objects.create(
                profile=self.customer,
                title=f"Order #{self.id} Cancelled",
                body=f"Your Order from {self.restaurant.restaurantName} was cancelled by the delivery partner",
                data=data,
            )
            Notification.objects.create(
                profile=self.restaurant,
                title=f"Order #{self.id} Cancelled",
                body=f"Order from {self.customer.user.first_name} {self.customer.user.last_name} was cancelled by the delivery partner",
                data=data,
            )
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})


class AcceptOrder(views.APIView):
    permission_classes = [IsRestaurantUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        data = {"open": "order", "id": f"{order.id}"}
        if order.status == "PL":
            order.status = "CK"
            order.save()
            Notification.objects.create(
                profile=self.customer,
                title=f"Order #{self.id} Accepted",
                body="Your Order was accepted by the restaurant",
            )
            Notification.objects.create(
                profile=self.deliveryMan,
                title=f"Order #{self.id} Accepted",
                body=f"Order from {self.restaurant.restaurantName} to {self.customer.user.first_name} {self.customer.user.last_name} that was assigned to you was accepted by the restaurant",
                data=data,
            )
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})


class OrderCookingFinished(views.APIView):
    permission_classes = [IsRestaurantUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        data = {"open": "order", "id": f"{order.id}"}
        if order.status == "CK":
            order.status = "WT"
            order.save()
            Notification.objects.create(
                profile=self.deliveryMan,
                title=f"Order #{self.id} Waiting for Pickup",
                body=f"Order from {self.restaurant.restaurantName} to {self.customer.user.first_name} {self.customer.user.last_name} is waiting to be picked up by you",
                data=data,
            )
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})


class OrderPickedUp(views.APIView):
    permission_classes = [IsDeliveryManUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        data = {"open": "order", "id": f"{order.id}"}
        if order.status == "WT":
            order.status = "PU"
            order.save()
            Notification.objects.create(
                profile=self.customer,
                title=f"Order #{self.id} Picked Up",
                body=f"Your Order from {self.restaurant.restaurantName} was picked up by {self.deliveryMan.user.first_name} {self.deliveryMan.user.last_name}",
                data=data,
            )
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})


class OrderArrived(views.APIView):
    permission_classes = [IsDeliveryManUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        data = {"open": "order", "id": f"{order.id}"}
        if order.status == "PU":
            order.status = "AR"
            order.save()
            Notification.objects.create(
                profile=self.customer,
                title=f"Order #{self.id} Arrived",
                body=f"{self.deliveryMan.user.first_name} {self.deliveryMan.user.last_name} arrived with your order from {self.restaurant.restaurantName}",
                data=data,
            )
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})


class OrderDelivered(views.APIView):
    permission_classes = [IsDeliveryManUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        data = {"open": "order", "id": f"{order.id}"}
        if order.status == "AR":
            order.status = "DL"
            order.paymentStatus = "RC"
            order.save()
            Notification.objects.create(
                profile=self.customer,
                title=f"Order #{self.id} Delivered",
                body=f"Your Order from {self.restaurant.restaurantName} was delivered",
                data=data,
            )
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})


class OrderPaidToRestaurant(views.APIView):
    permission_classes = [IsDeliveryManUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        if order.paymentStatus == "RC":
            order.paymentStatus = "WT"
            order.save()
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})


class OrderPaidToRestaurantConfirm(views.APIView):
    permission_classes = [IsDeliveryManUser]

    def post(self, request):
        order = Order.objects.get(pk=request.POST.get("id"))
        if order.paymentStatus == "WT":
            order.paymentStatus = "CM"
            order.save()
        else:
            return Response({"detail": "Invalid user or order status"}, status=400)
        return Response({"success": "Order successfully cancelled"})
