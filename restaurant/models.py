from django.db import models
from user.models import Profile
from cloudinary.models import CloudinaryField


def public_id(instance):
    return f"Product_{instance.id}"


# Create your models here.
class Product(models.Model):
    name = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    nonveg = models.BooleanField(default=False)
    category = models.CharField(max_length=64, default="Others")
    restaurant = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="menu",
        limit_choices_to={"kind": "R"},
    )
    image = CloudinaryField(
        "image", upload_preset="FoodExDjango", public_id=public_id, blank=True
    )
    available = models.BooleanField(default=True)

    def product(self):
        return "{} | {} | {}".format(
            self.name, self.restaurant.restaurantName, self.category
        )

    def __str__(self):
        return self.product()


class Variant(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )
    name = models.CharField(max_length=32, null=False, default="default")
    price = models.FloatField(null=False)

    class Meta:
        unique_together = (
            "name",
            "product",
        )

    def variant(self):
        return "{} | {} | {}".format(self.name, self.product, self.price)

    def __str__(self):
        return self.variant()
