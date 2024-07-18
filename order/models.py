from django.db import models
from restaurant.models import Product
from user.models import Profile
from asgiref.sync import async_to_sync
from google.oauth2 import service_account
import google.auth.transport.requests
import firebase_admin
from firebase_admin import credentials, messaging
import json
import asyncio
import os

cred = credentials.Certificate(
    {
        "type": os.getenv('FIREBASE_ACCOUNT_TYPE'),
        "project_id": os.getenv('FIREBASE_PROJECT_ID'),
        "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": os.getenv('FIREBASE_PRIVATE_KEY'),
        "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.getenv('FIREBASE_CLIENT_ID'),
        "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
        "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
        "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN')
    }
)
firebase_admin.initialize_app(cred)


# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ("PL", "Placed"),
        ("CK", "Cooking"),
        ("WT", "Waiting for Pickup"),
        ("PU", "Picked Up"),
        ("AR", "Arrived at location"),
        ("DL", "Delivered"),
        ("XC", "Cancelled"),
        ("XR", "Cancelled by restaurant"),
        ("XD", "Cancelled by delivery partner"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("NP", "Not paid by customer"),
        ("RC", "Received Payment from Customer"),
        ("WT", "Waiting for Confirmation by Restaurant"),
        ("CM", "Completed"),
    ]

    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default="PL")
    paymentStatus = models.CharField(
        max_length=2, choices=PAYMENT_STATUS_CHOICES, default="NP"
    )
    cancelledReason = models.TextField(null=True, blank=True, default=None)
    content = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    productTotal = models.FloatField()
    deliveryCharge = models.IntegerField()
    restaurant = models.ForeignKey(
        Profile,
        null=True,
        on_delete=models.SET_NULL,
        related_name="ordersReceived",
        limit_choices_to={"kind": "R"},
    )
    customer = models.ForeignKey(
        Profile,
        null=True,
        on_delete=models.SET_NULL,
        related_name="ordersPlaced",
        limit_choices_to={"kind": "C"},
    )
    deliveryMan = models.ForeignKey(
        Profile,
        null=True,
        on_delete=models.SET_NULL,
        related_name="ordersDelivered",
        limit_choices_to={"kind": "D"},
    )
    placedOn = models.DateTimeField(auto_now_add=True)
    lastUpdateOn = models.DateTimeField(auto_now=True)

    def order(self):
        return "{} | {} | {} | {}".format(
            self.status,
            self.restaurant.restaurantName,
            self.customer.restaurantName,
            self.placedOn,
        )

    def __str__(self):
        return self.order()


class Notification(models.Model):
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.TextField(default="Notification Title")
    body = models.TextField(default="Notification Body")
    data = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        fcmtoken = self.profile.fcmtoken
        if fcmtoken != None:
            message = messaging.Message(
                notification=messaging.Notification(
                    title=self.title,
                    body=self.body,
                ),
                data=self.data,
                token=self.profile.fcmtoken,
            )
            asyncio.run(self.sendMessage(message, *args, **kwargs))

    async def sendMessage(self, message, *args, **kwargs):
        try:
            messaging.send(message)
        except:
            super(Notification, self).save(*args, **kwargs)
