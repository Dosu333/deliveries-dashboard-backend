from attr import field
from rest_framework import serializers
from email_validator import validate_email, EmailNotValidError
from .models import *
from .utils import split_datetime_object


class OffStoreDeliverySerializer(serializers.ModelSerializer):
    order_placed_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    # pickup_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
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


class ItemPickedSerialaizer(serializers.ModelSerializer):

    class Meta:
        model = ItemsPicked
        exclude = ['order', ]


class LogisticsCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogisticsCompany
        exclude = ['id', 'serviceable_pickup_cities', 'serviceable_dropoff_cities', 'cities_with_most_reliable_service']


class AvailableLogisticsCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailableLogisticsForOrder
        exclude = ['order', 'selected']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        logistics_company = LogisticsCompany.objects.get(id=str(representation['logistics_company']))
        logistics_company = LogisticsCompanySerializer(logistics_company).data
        representation['logistics_company'] = logistics_company['name']
        representation['code'] = logistics_company['code']
        representation['image'] = logistics_company['image']
        representation['pickup_eta'] = "Next working day"
        representation['tracking_url'] = logistics_company['tracking_url']
        return representation


class ListAPIDeliverySerializer(serializers.ModelSerializer):
    order_placed_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    # pickup_time = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S")
    intransit_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    dispatched_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    delivered_at = serializers.DateTimeField(format="%d-%m-%Y %H:%M:%S", required=False)
    itempicked = ItemPickedSerialaizer(many=True)

    class Meta:
        model = APIDelivery
        fields = ('__all__')


class CreateAPIDeliverySerializer(serializers.ModelSerializer):
    itempicked = ItemPickedSerialaizer(many=True)

    class Meta:
        model = APIDelivery
        exclude = ['delivery_type', 'total_weight', 'business_id', 'logistics_company_code', 'number_of_items', 'amount_paid', 'shipping_type', 'transaction_reference', 'tracking_id', 'delivery_date', 'paid', 'dispatched_at', 'intransit_at', 'delivered_at', 'status']

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

    def create(self, validated_data):
        items_picked = validated_data.pop('itempicked')
        order = APIDelivery.objects.create(**validated_data)
        total_weight = 0
        number_of_items = 0

        for item in items_picked:
            total_weight = total_weight + (float(item['weight']) * float(item['quantity']))
            number_of_items = number_of_items + float(item['quantity'])
            ItemsPicked.objects.create(order=order, **item)

        total_weight = round(total_weight, 1)

        while total_weight % 0.5 != 0:
            total_weight = round(total_weight + 0.1, 1)

        order.total_weight = total_weight
        order.number_of_items = number_of_items
        order.save()

        return order


class RatesSerializer(serializers.Serializer):
    rate_id = serializers.UUIDField()

    def validate(self, attrs):
        rate_id = attrs['rate_id']

        if not AvailableLogisticsForOrder.objects.filter(rate_id=str(rate_id)).exists():
            raise serializers.ValidationError("Selected rate does not exist")
        return super().validate(attrs)

class ShippingVariablesSerializer(serializers.Serializer):
    merchant_state = serializers.CharField(required=True)
    receiver_state = serializers.CharField(required=True)
    merchant_address = serializers.CharField(required=False)
    receiver_address = serializers.CharField(required=False)
    weight = serializers.DecimalField(max_digits=4, decimal_places=1, required=True)
    shipping_type = serializers.CharField(required=True)


class TrackDeliverySerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    delivery_id = serializers.UUIDField(required=True)

    def validate(self, attrs):
        request_from = attrs.get('type', None)

        if request_from and request_from not in ['store', 'offstore', 'api']:
            raise serializers.ValidationError('Invalid delivery type.')
        return super().validate(attrs)