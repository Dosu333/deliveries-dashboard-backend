from decimal import Clamped
from time import strftime
from rest_framework import views, viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from twilio.rest import Client
from user.utils import get_user_data, get_user_store_orders
from .shipping_fee.shipping import calculate_shipping_fee, calculate_shipping_rates
from .utils import split_datetime_object
from .models import *
from .serializers import *
from .tasks import send_alert_updates
import os
import requests
import datetime


class GetShippingFee(views.APIView):
    """"Get shipping fee for offstore and store deliveries"""
    serializer_class = ShippingVariablesSerializer

    def post(self, request, *args, **kwargs):
        # try:
        items = request.data.get('items', None)
        if not items:
            merchant_address = request.data.get('merchant_address', None)
            receiver_address = request.data.get('receiver_address', None)

            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                fee = calculate_shipping_fee(
                    total_weight=request.data['weight'], merchant_state=request.data['merchant_state'], receiver_state=request.data['receiver_state'], merchant_address=merchant_address, receiver_address=receiver_address, shipping_type=request.data['shipping_type'])

                if fee['success']:
                    return Response({'success': True, 'shipping_fee': fee['fee']}, status=status.HTTP_200_OK)
                return Response({'success': False, 'shipping_fee': fee['fee'], 'error': fee['message']}, status=status.HTTP_200_OK)
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # except Exception as e:
        #     return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TrackDeliveryView(views.APIView):
    """Track instore and offstore deliveries"""
    serializer_class = TrackDeliverySerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            checkpoint_data = ['order_placed_at',
                               'dispatched_at', 'intransit_at', 'delivered_at']
            checkpoints = []

            if serializer.is_valid():
                if serializer.data['type'] == 'offstore':
                    delivery = OffStoreDelivery.objects.get(
                        id=str(serializer.data['delivery_id']))
                    delivey_data = OffStoreDeliverySerializer(delivery).data

                    for checkpoint in checkpoint_data:
                        checkpoints.append(
                            {'status': checkpoint[:-3], 'date_time': delivey_data[checkpoint]})
                    return Response({'success': True, 'checkpoints': checkpoints}, status=status.HTTP_200_OK)

                if serializer.data['type'] == 'store':
                    url = f"https://api.boxin.ng/api/v1/store/orders/{serializer.data['delivery_id']}/"
                    res = requests.get(url, verify=False)
                    response = res.json()

                    for checkpoint in checkpoint_data:
                        checkpoints.append(
                            {'status': checkpoint[:-3], 'date_time': response[checkpoint]})
                    return Response({'success': True, 'checkpoints': checkpoints}, status=status.HTTP_200_OK)
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OffStoreDeliveryViewSet(viewsets.ModelViewSet):
    """Offstore orders viewsets"""

    queryset = OffStoreDelivery.objects.all()
    serializer_class = OffStoreDeliverySerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['customer_name', 'customer_email',
                     'customer_phone', 'destination_state', 'pickup_state']

    def get_queryset(self):
        return self.queryset.filter(business_id=self.request.user.id)

    def perform_create(self, serializer):
        instance = serializer.save()
        obj = self.queryset.get(pk=instance.id)
        obj.business_id = self.request.user.id
        obj.save()


class UpdateOffstoreDeliveryView(views.APIView):
    """Update status of delivery"""

    def get(self, request, *args, **kwargs):
        ref = request.query_params.get('ref', None)
        amount = request.query_params.get('amount', None)
        try:
            if ref:
                obj = OffStoreDelivery.objects.get(
                    transaction_reference=ref)
                if obj.status == 'AWAITING PAYMENT':
                    obj.status = 'PENDING'
                    obj.amount_paid = float(amount)/100
                    obj.save()
                    delivery_object = OffStoreDeliverySerializer(obj).data
                    send_alert_updates.delay(delivery_object)
                return Response({'success': True}, status=status.HTTP_200_OK)
            return Response({'success': False, 'error': 'No transaction references'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetStoreDeliveriesView(views.APIView):
    """Get instore orders of user"""

    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        try:
            store_orders = get_user_store_orders(request.user.id)
            if store_orders:
                return Response(store_orders, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyTransaction(views.APIView):
    url = 'https://api.paystack.co/transaction/verify/'

    def get(self, request, *args, **kwargs):
        ref = self.request.query_params.get('reference', None)

        if ref is not None:
            self.url = self.url + ref
            headers_dict = {'Authorization': "Bearer {}".format(
                os.environ.get('PAYSTACK_SECRET_KEY'))}

            try:
                r = requests.get(self.url, headers=headers_dict)
                response = r.json()

                if response['status']:
                    if response['data']['status'] == 'success':
                        obj = OffStoreDelivery.objects.get(
                        transaction_reference=ref)

                        if obj.status == 'AWAITING PAYMENT':
                            obj.status = 'PENDING'
                            obj.amount_paid = float(
                                response['data']['amount']) / 100
                            obj.save()
                            delivery_object = OffStoreDeliverySerializer(obj).data
                            send_alert_updates.delay(delivery_object)
                        return Response({'success': True}, status=status.HTTP_200_OK)

                    return Response({'success': False}, status=status.HTTP_200_OK)

                return Response({'success': False, 'errors': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'error': 'no ref'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class GetRatesAPIView(views.APIView):
    """This endpoint creates an order and returns the order id and the logistics companies that can service the orders with their respective rates and ETA"""
    serializer_class = APIDeliverySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            available_logistics = LogisticsCompany.objects.filter(Q(serviceable_pickup_cities__contains=[str(instance.pickup_state).lower()]) & Q(serviceable_dropoff_cities__contains=[str(instance.destination_state).lower()]))
            available_logistics_data = LogisticsCompanySerializer(available_logistics, many=True).data

            for company in available_logistics:
                fee = calculate_shipping_rates(merchant_address=instance.pickup_address, merchant_state=instance.pickup_state, receiver_address=instance.destination_address, receiver_state=instance.destination_state, total_weight=instance.total_weight, logistics_company=company.name)
                AvailableLogisticsForOrder.objects.create(logistics_company=company, total_fee=fee['fee'], order=instance)

            logistics = AvailableLogisticsForOrder.objects.filter(order=instance)
            available_logistics_data = AvailableLogisticsCompanySerializer(logistics, many=True).data

            data = {
                'order_id': instance.id,
                'available_logistics': available_logistics_data
            }
            return Response({'success': True, 'data': data}, status=status.HTTP_200_OK)
        return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_200_OK)

