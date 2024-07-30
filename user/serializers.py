from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Profile, Phone, Email


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField(required=True, write_only=True)
    password = serializers.CharField(required=True, write_only=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields[self.username_field] = serializers.CharField(required=False, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('No user found with this email address.')

        if not user.check_password(password) or not Email.objects.get(email=email).valid():
            raise serializers.ValidationError('Incorrect password.')

        attrs['username'] = user.username
        return super().validate(attrs)


class ProfileBaseSerializer(serializers.ModelSerializer):
    image = serializers.FileField(use_url=True)

    class Meta:
        model = Profile
        fields = "__all__"
        extra_kwargs = {"fcmtoken": {"write_only": True}}


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileBaseSerializer()

    class Meta:
        depth = 1
        model = User
        fields = [
            "id",
            "last_login",
            "profile",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
        ]


class ProfileSerializer(ProfileBaseSerializer):
    user = UserSerializer()


class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ["number"]


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Email
        fields = ["email"]
