from attr import field
from rest_framework import serializers
from email_validator import validate_email, EmailNotValidError
from .models import *
from .utils import split_datetime_object


class OffStoreDeliverySerializer(serializers.ModelSerializer):
    order_placed_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    pickup_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    intransit_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    dispatched_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    delivered_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)

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


class TrackDeliverySerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    delivery_id = serializers.UUIDField(required=True)

    def validate(self, attrs):
        request_from = attrs.get('type', None)

        if request_from and request_from not in ['store', 'offstore']:
            raise serializers.ValidationError('Invalid delivery type.')
        return super().validate(attrs)