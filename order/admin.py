try:

    from django.contrib import admin
    from .models import Order, Notification

    # Register your models here.
    admin.site.register(Order)
    admin.site.register(Notification)

except:
    pass
