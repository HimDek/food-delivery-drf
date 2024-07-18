import json
from rest_framework import serializers
from .models import Order
from user.serializers import ProfileSerializer

class OrderSerializer(serializers.ModelSerializer):
    entries = serializers.SerializerMethodField()
    customer = ProfileSerializer()
    restaurant = ProfileSerializer()
    deliveryMan = ProfileSerializer()

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
