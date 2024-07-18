import json
from rest_framework import serializers
from django.contrib.auth.models import User
from random import randint
from .models import *
from user.serializers import ProfileSerializer

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.FileField(use_url=True)
    restaurant = ProfileSerializer()

    class Meta:
        depth = 1
        model = Product
        fields = [ 'id', 'name', 'description', 'nonveg', 'category', 'restaurant', 'available', 'image', 'variants' ]
        extra_kwargs = { 'description': {'required': False}, 'variants': {'required': True} }