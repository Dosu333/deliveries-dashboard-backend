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
from rest_framework_api_key.permissions import HasAPIKey
from rest_framework_api_key.models import APIKey
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

                if serializer.data['type'] == 'api':
                    delivery = APIDelivery.objects.get(
                        id=str(serializer.data['delivery_id']))
                    delivey_data = ListAPIDeliverySerializer(delivery).data

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
        type = request.query_params.get('type', None)

        try:
            if ref:
                if type == 'offstore':
                    obj = OffStoreDelivery.objects.get(
                        transaction_reference=ref)
                    if obj.status == 'AWAITING PAYMENT':
                        obj.status = 'PENDING'
                        obj.amount_paid = float(amount)/100
                        obj.save()
                        delivery_object = OffStoreDeliverySerializer(obj).data
                        send_alert_updates.delay(delivery_object)
                    return Response({'success': True}, status=status.HTTP_200_OK)
                elif type == 'api':
                    rate = AvailableLogisticsForOrder.objects.get(id=ref)
                    rate.order.transaction_reference = ref
                    rate.order.save()

                    if rate.order.status == 'AWAITING PAYMENT' and float(amount)/100 >= float(rate.total_fee):
                        rate.order.status = 'PENDING'
                        rate.order.amount_paid = float(amount)/100
                        rate.order.save()
                        delivery_object = ListAPIDeliverySerializer(obj).data
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
                            delivery_object = OffStoreDeliverySerializer(
                                obj).data
                            send_alert_updates.delay(delivery_object)
                        return Response({'success': True}, status=status.HTTP_200_OK)

                    return Response({'success': False}, status=status.HTTP_200_OK)

                return Response({'success': False, 'errors': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'error': 'no ref'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetRatesAPIView(views.APIView):
    """This endpoint creates an order and returns the order id and the logistics companies that can service the orders with their respective rates and ETA"""
    serializer_class = CreateAPIDeliverySerializer
    permission_classes = [HasAPIKey | IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        try:
            if serializer.is_valid():
                key = request.META["HTTP_AUTHORIZATION"].split()[1]
                instance = serializer.save()

                try: 
                    api_key = APIKey.objects.get_from_key(key)
                    instance.business_id = api_key.name
                except:
                    instance.business_id = request.user.id
                instance.save()

                available_logistics = LogisticsCompany.objects.all()

                for company in available_logistics:
                    fee = calculate_shipping_rates(merchant_address=instance.pickup_address, merchant_state=instance.pickup_state, receiver_address=instance.destination_address, merchant_city=instance.pickup_city, receiver_city=instance.destination_city,
                                                receiver_state=instance.destination_state, total_weight=instance.total_weight, logistics_company=company.name.lower())
                    
                    if fee['fee']:
                        AvailableLogisticsForOrder.objects.create(
                            logistics_company=company, total_fee=fee['fee'], order=instance, delivery_duration=fee['delivery_eta'])

                logistics = AvailableLogisticsForOrder.objects.filter(
                    order=instance)
                available_logistics_data = AvailableLogisticsCompanySerializer(
                    logistics, many=True).data
                return Response({'success': True, 'data': available_logistics_data}, status=status.HTTP_200_OK)
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'success':False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MakePaymentForAPIDeliveryView(views.APIView):
    """This endpoint allows for a rate to be selected and paid for via wallet"""
    queryset = AvailableLogisticsForOrder.objects.all()

    def get(self, request, *args, **kwargs):
        rate = self.request.query_params.get('rate', None)

        try:
            if rate and self.queryset.filter(id=str(rate)).exists():
                rate = self.queryset.get(id=str(rate))
                rate.selected = True
                rate.order.paid = True
                rate.order.save()
                rate.save()
                return Response({'success': True, 'message': 'Payment successful'}, status=status.HTTP_200_OK)
            return Response({'success':False, 'error': "Rate does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response ({'success':False, 'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

