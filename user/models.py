from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timezone
from math import cos, pi
from cloudinary.models import CloudinaryField


def public_id(instance):
    return f"Profile_{instance.id}"


# Create your models here.


class Profile(models.Model):
    KIND_CHOICES = [
        ("C", "Customer"),
        ("R", "Restaurant"),
        ("D", "Delivery Man"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    verified = models.BooleanField(default=False)
    restaurantName = models.CharField(max_length=32, blank=True)
    joinedOn = models.DateField(auto_now_add=True)
    lastActiveOn = models.DateTimeField(auto_now=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True
    )
    kind = models.CharField(max_length=1, choices=KIND_CHOICES, default="C")
    available = models.BooleanField(default=False)
    image = CloudinaryField(
        "image", upload_preset="FoodExDjango", public_id=public_id, blank=True
    )
    fcmtoken = models.TextField(null=True, unique=True, blank=True)
    upiID = models.CharField(max_length=32, blank=True)

    @classmethod
    def objects_within_square(self, center_lat, center_lon, size_km):
        center_lat = float(center_lat)
        center_lon = float(center_lon)
        # Calculate the bounding square for the given size
        lat_degree = size_km / 110.574
        lon_degree = size_km / (111.320 * cos(center_lat * (pi / 180)))

        min_lat = center_lat - lat_degree
        max_lat = center_lat + lat_degree
        min_lon = center_lon - lon_degree
        max_lon = center_lon + lon_degree

        # Construct the SQL query to filter objects within the bounding square
        return self.objects.extra(
            where=[
                "latitude BETWEEN %s AND %s",
                "longitude BETWEEN %s AND %s",
            ],
            params=[min_lat, max_lat, min_lon, max_lon],
        )

    def profile(self):
        return "{} {} ({})".format(
            self.user.first_name, self.user.last_name, self.user.username
        )

    def __str__(self):
        return self.profile()


class Phone(models.Model):
    number = models.CharField(max_length=10, null=False, unique=True)
    otp = models.PositiveIntegerField(null=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def valid(self):
        return (
            True
            if (datetime.now(timezone.utc) - self.updatedOn).seconds / 60 < 5
            else False
        )


class Email(models.Model):
    email = models.EmailField(null=False, unique=True)
    otp = models.PositiveIntegerField(null=True)
    updatedOn = models.DateTimeField(auto_now=True)

    def valid(self):
        return (
            True
            if (datetime.now(timezone.utc) - self.updatedOn).seconds / 60 < 5
            else False
        )
