import json
from rest_framework import serializers
from django.contrib.auth.models import User
from random import randint
from .models import *
from restaurant.models import Product, Variant
from user.models import Profile
from user.serializers import ProfileSerializer
import requests
import math

class OrderSerializer(serializers.ModelSerializer):
    entries = serializers.SerializerMethodField()
    customer = ProfileSerializer()
    restaurant = ProfileSerializer()
    delivryMan = ProfileSerializer()

    def get_entries(self, obj):
        content = json.loads(obj.content)
        entries = []
        for entry in content:
            if len(entry['variants']) > 0:
                entries.append(entry)
                entry['subtotal'] = 0
                for variant in entry['variants']:
                    entry['subtotal'] += variant['price']
        return entries

    class Meta:
        depth = 2
        model = Order
        fields = '__all__'
