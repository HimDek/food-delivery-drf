# from django.shortcuts import render
from rest_framework import generics, views
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import *
from .serializers import *
from .permissions import *

# Create your views here.


class CreateUsers(views.APIView):
    def post(self, request):
        if not request.POST.get('phone'):
            error = {'detail': 'Phone number is required'}
            return Response(error, status=400)
        elif not request.POST.get('otp'):
            error = {'detail': 'Phone OTP is required'}
            return Response(error, status=400)
        elif not request.POST.get('first_name'):
            error = {'detail': 'First name is required'}
            return Response(error, status=400)
        elif not Phone.objects.filter(number=request.POST.get('phone')).exists():
            error = {'detail': 'Invalid phone OTP'}
            return Response(error, status=400)
        elif User.objects.filter(username=request.POST.get('phone')).exists():
            error = {'detail': 'Account with that phone number already exist'}
            return Response(error, status=400)
        else:
            phone = Phone.objects.get(
                number=request.POST.get('phone'))
            if not phone.valid() or '{}'.format(phone.otp) != request.POST.get('otp'):
                error = {'detail': 'Invalid phone OTP'}
                return Response(error, status=400)
            else:
                user = User.objects.create(username=request.POST.get('phone'), first_name=request.POST.get(
                    'first_name'), last_name=request.POST.get('last_name'))
                profile = Profile.objects.create(
                    user=user)
                user.set_password(request.POST.get('otp'))
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
        if request.POST.get('restaurantname'):
            profile.restaurantName = request.POST.get('restaurantname')
        if request.POST.get('first_name'):
            user.first_name = request.POST.get('first_name')
        if request.POST.get('last_name'):
            user.last_name = request.POST.get('last_name')
        if request.POST.get('available'):
            profile.available = True if request.POST.get(
                'available') == 'true' else False
        if request.POST.get('fcmtoken'):
            for obj in Profile.objects.filter(fcmtoken=request.POST.get('fcmtoken')):
                obj.fcmtoken = None
                obj.save()
            profile.fcmtoken = request.POST.get('fcmtoken')
        if request.POST.get('upiID'):
            profile.upiID = request.POST.get('upiID')
        if request.FILES.get('image'):
            profile.image = request.FILES.get('image')

        profile.save()
        user.save()
        return Response(ProfileSerializer(profile).data)


class GetOTP(views.APIView):
    def post(self, request):
        phone, created = Phone.objects.update_or_create(
            number=request.POST.get('number'),
            defaults={'number': request.POST.get(
                'number'), 'otp': randint(100000, 999999)}
        )
        if User.objects.filter(username=phone.number).exists():
            user = User.objects.get(username=phone.number)
            user.set_password('{}'.format(phone.otp))
            user.save()

        print({phone.number: phone.otp})
        return Response(PhoneSerializer(phone).data)
