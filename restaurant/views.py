from rest_framework import generics, views
from rest_framework.response import Response
from django.db.models import F, Func, FloatField
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User
from django.contrib.postgres.search import SearchVector

from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import *
from .serializers import *
from .permissions import *
from user.models import Profile
from user.serializers import ProfileSerializer
import requests
import math
import json

# Create your views here.


class ListRestaurants(generics.ListAPIView):
    serializer_class = ProfileSerializer

    def get_queryset(self):
        return Profile.objects_within_square(self.request.query_params.get('latitude'), self.request.query_params.get('longitude'), 20).filter(kind='R')


class ListCreateProducts(generics.ListCreateAPIView):
    permission_classes = [IsInProfileMenuOrReadOnly]
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.all()
        restaurant = self.request.query_params.get('restaurant')
        if restaurant is not None:
            queryset = queryset.filter(restaurant=restaurant)
        return queryset

    def post(self, request):
        name = request.POST.get('name')
        restaurant = request.user.profile

        if request.POST.get('description'):
            description = request.POST.get('description')
        else:
            description = ""

        if request.POST.get('category'):
            category = request.POST.get('category')
        else:
            category = ""

        nonveg = True if request.POST.get('nonveg') == 'true' else False

        if request.FILES.get('image'):
            image = request.FILES.get('image')
        else:
            image = None

        product = Product.objects.create(
            restaurant=restaurant, name=name, description=description, category=category, image=image)

        if request.POST.get('variants'):
            variants = json.loads(request.POST.get('variants'))

            for variant in variants:
                Variant.objects.create(
                    name=variant['name'], price=variant['price'], product=product)

        return Response(ProductSerializer(product).data)


class RetrieveUpdateProduct(generics.RetrieveUpdateAPIView):
    permission_classes = [IsInProfileMenuOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def patch(self, request, pk):
        product = Product.objects.get(id=pk)

        if request.POST.get('name'):
            product.name = request.POST.get('name')

        if request.POST.get('description'):
            product.description = request.POST.get('description')

        if request.POST.get('category'):
            product.category = request.POST.get('category')

        if request.POST.get('nonveg'):
            product.nonveg = True if request.POST.get(
                'nonveg') == 'true' else False

        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        if request.POST.get('variants'):
            variants = json.loads(request.POST.get('variants'))
            for variant in Variant.objects.filter(product=product):
                variant.delete()

            for variant in variants:
                Variant.objects.create(
                    name=variant['name'], price=variant['price'], product=product)

        product.save()

        return Response(ProductSerializer(product).data)


class BulkDeleteProducts(views.APIView):
    def post(self, request):
        for product in json.loads(request.POST.get('products')):
            try:
                Product.objects.get(id=product).delete()
            except:
                pass
        return Response({'detail': 'products deleted'})


class BulkAvailableProducts(views.APIView):
    def post(self, request):
        for product in json.loads(request.POST.get('products')):
            try:
                product = Product.objects.get(id=product)
                product.available = True
                product.save()
            except:
                pass
        return Response({'detail': 'products availability updated'})


class BulkUnavailableProducts(views.APIView):
    def post(self, request):
        for product in json.loads(request.POST.get('products')):
            try:
                product = Product.objects.get(id=product)
                product.available = False
                product.save()
            except:
                pass
        return Response({'detail': 'products availability updated'})


class GetDeliveryCharge(views.APIView):
    def post(self, request):
        restaurant = Profile.objects.get(id=request.POST.get('restaurant'))
        latitude1 = restaurant.latitude
        longitude1 = restaurant.longitude
        latitude2 = request.POST.get('latitude')
        longitude2 = request.POST.get('longitude')

        url = f'http://dev.virtualearth.net/REST/v1/Routes?wayPoint.1={latitude1},{longitude1}&wayPoint.2={latitude2},{longitude2}&optimize=timeWithTraffic&travelMode=Driving&key=Avp1HW_M-FcjR-yGlkZxwSGjBoMpHZejnAB1XjcCqh23apgSMBoaaNJ3_CZDdqYy'
        response = requests.get(url).json()
        distance = None
        if len(response['resourceSets']):
            if len(response['resourceSets'][0]['resources']):
                distance = response['resourceSets'][0]['resources'][0]['travelDistance']

        if distance == None:
            return Response({'value': 0, 'detail': 'does not deliver to this location'})

        else:
            delivery_charge = math.ceil(20+(5*distance))
            return Response({'value': delivery_charge, 'info': 'delivery charge calculated based on distance'})


class Search(views.APIView):
    def get(self, request):
        query = request.query_params.get('query')
        products = Product.objects.annotate(
            search=SearchVector('name', 'description', 'category'),).filter(search=query)

        return Response(ProductSerializer(products, many=True).data)
