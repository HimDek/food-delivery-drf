from rest_framework import serializers
from django.contrib.auth.models import User
from random import randint
from .models import *


class ProfileBaseSerializer(serializers.ModelSerializer):
    image = serializers.FileField(use_url=True)

    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {'fcmtoken': {'write_only': True}}


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileBaseSerializer()

    class Meta:
        depth = 1
        model = User
        fields = ['id', 'last_login', 'profile', 'username', 'first_name',
                  'last_name', 'date_joined']


class ProfileSerializer(ProfileBaseSerializer):
    user = UserSerializer()

class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ['number']
