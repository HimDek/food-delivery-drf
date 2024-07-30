import os
import requests
from random import randint
from rest_framework import views
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from rest_framework.permissions import IsAuthenticated
from .models import Profile, Phone, Email
from .serializers import (
    UserSerializer,
    ProfileSerializer,
    PhoneSerializer,
    EmailSerializer,
)

# Create your views here.


class CreateUsers(views.APIView):
    def post(self, request):
        if not request.POST.get("phone"):
            error = {"detail": "Phone number is required"}
            return Response(error, status=400)
        elif not request.POST.get("phoneotp"):
            error = {"detail": "Phone OTP is required"}
            return Response(error, status=400)
        elif not request.POST.get("email"):
            error = {"detail": "Email is required"}
            return Response(error, status=400)
        elif not request.POST.get("emailotp"):
            error = {"detail": "Email OTP is required"}
            return Response(error, status=400)
        elif not request.POST.get("first_name"):
            error = {"detail": "First name is required"}
            return Response(error, status=400)
        elif not Phone.objects.filter(number=request.POST.get("phone")).exists():
            error = {"detail": "Invalid phone OTP"}
            return Response(error, status=400)
        elif User.objects.filter(username=request.POST.get("phone")).exists():
            error = {"detail": "Account with that phone number already exist"}
            return Response(error, status=400)
        elif User.objects.filter(email=request.POST.get("email")).exists():
            error = {"detail": "Account with that email already exist"}
            return Response(error, status=400)
        else:
            phone = Phone.objects.get(number=request.POST.get("phone"))
            email = Email.objects.get(email=request.POST.get("email"))
            if not phone.valid() or "{}".format(phone.otp) != request.POST.get("phoneotp"):
                error = {"detail": "Invalid phone OTP"}
                return Response(error, status=400)
            elif not email.valid() or "{}".format(email.otp) != request.POST.get("emailotp"):
                error = {"detail": "Invalid email OTP"}
                return Response(error, status=400)
            else:
                user = User.objects.create(
                    email=request.POST.get("email"),
                    username=request.POST.get("phone"),
                    first_name=request.POST.get("first_name"),
                    last_name=request.POST.get("last_name"),
                )
                profile = Profile.objects.create(user=user)
                user.set_password(request.POST.get("emailotp"))
                user.save()
                profile.save()

        return Response(UserSerializer(user).data)


class RetrieveSelfUser(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class RetrieveUpdateSelfUserProfile(views.APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(ProfileSerializer(request.user.profile).data)

    def patch(self, request):
        profile = request.user.profile
        user = request.user
        if request.POST.get("restaurantname"):
            profile.restaurantName = request.POST.get("restaurantname")
        if request.POST.get("first_name"):
            user.first_name = request.POST.get("first_name")
        if request.POST.get("last_name"):
            user.last_name = request.POST.get("last_name")
        if request.POST.get("available"):
            profile.available = (
                True if request.POST.get("available") == "true" else False
            )
        if request.POST.get("fcmtoken"):
            for obj in Profile.objects.filter(fcmtoken=request.POST.get("fcmtoken")):
                obj.fcmtoken = None
                obj.save()
            profile.fcmtoken = request.POST.get("fcmtoken")
        if request.POST.get("upiID"):
            profile.upiID = request.POST.get("upiID")
        if request.FILES.get("image"):
            profile.image = request.FILES.get("image")
        if request.POST.get("phone") and request.POST.get("otp"):
            phone = Phone.objects.get(phone=request.POST.get("phone"))
            if request.POST.get("otp") == phone.otp and phone.valid():
                user.username = request.POST.get("phone")
        if request.POST.get("email") and request.POST.get("emailotp"):
            email = Phone.objects.get(email=request.POST.get("email"))
            if request.POST.get("emailotp") == email.otp and email.valid():
                user.email = request.POST.get("email")

        profile.save()
        user.save()
        return Response(ProfileSerializer(profile).data)


class GetPhoneOTP(views.APIView):
    def post(self, request):
        phone, created = Phone.objects.update_or_create(
            number=request.POST.get("number"),
            defaults={
                "number": request.POST.get("number"),
                "otp": randint(100000, 999999),
            },
        )

        print({phone.number: phone.otp})
        url = f"https://2factor.in/API/V1/{os.getenv('TWO_FACTOR_API_KEY')}/SMS/{phone.number}/{phone.otp}/OTP1"
        response = requests.get(url).json()
        return Response(PhoneSerializer(phone).data, status=response.status_code)


class GetEmailOTP(views.APIView):
    def post(self, request):
        email, created = Email.objects.update_or_create(
            email=request.POST.get("email"),
            defaults={
                "email": request.POST.get("email"),
                "otp": randint(100000, 999999),
            },
        )
        if User.objects.filter(email=email.email).exists():
            user = User.objects.get(email=email.email)
            user.set_password("{}".format(email.otp))
            user.save()

        print({email.email: email.otp})
        html_message = render_to_string(
            "email_otp.html",
            {
                "otp": email.otp
            },
        )
        sent = send_mail(
            subject="Email OTP for Maaco",
            message=strip_tags(html_message),
            from_email=None,
            recipient_list=[email.email],
            html_message=html_message,
        )
        if sent:
            return Response(EmailSerializer(email).data)
        else:
            return Response(EmailSerializer(email).data, status=503)
