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