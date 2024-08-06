from rest_framework import serializers
from .models import BaseModel


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = ('event', 'price', 'date')

    def validate_price(self, value):
        try:
            float(value)
            return value
        except ValueError:
            raise serializers.ValidationError('Invalid Price')
