from attr import field
from rest_framework import serializers
from email_validator import validate_email, EmailNotValidError
from .models import *


class OffStoreDeliverySerializer(serializers.ModelSerializer):
    class Meta:
        model = OffStoreDelivery
        fields = ('__all__')

    def validate(self, attrs):
        email = attrs.get('customer_email', None)
        if email:
            email = attrs['customer_email'].lower().strip()
            try:
                valid = validate_email(attrs['customer_email'])
                attrs['customer_email'] = valid.email
                return super().validate(attrs)
            except EmailNotValidError as e:
                raise serializers.ValidationError(e)
        return super().validate(attrs)


class ShippingVariablesSerializer(serializers.Serializer):
    merchant_state = serializers.CharField(required=True)
    receiver_state = serializers.CharField(required=True)
    weight = serializers.DecimalField(max_digits=4, decimal_places=1, required=True)
    shipping_type = serializers.CharField(required=True)