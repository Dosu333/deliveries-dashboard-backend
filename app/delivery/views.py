from decimal import Clamped
from rest_framework import views, viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from user.utils import get_user_data, get_user_store_orders
from .shipping_fee.shipping import calculate_shipping_fee
from .utils import split_datetime_object
from .models import *
from .serializers import *
import os
import requests


class GetShippingFee(views.APIView):
    """"Get shipping fee for offstore and store deliveries"""
    serializer_class = ShippingVariablesSerializer

    def post(self, request, *args, **kwargs):
        try:
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
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                delivery = OffStoreDelivery.objects.get(
                    transaction_reference=ref)
                delivery.status = 'PENDING'
                delivery.amount_paid = float(amount)/100
                delivery.save()
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
                os.environ.get('PAYSTACK_TEST_SECRET_KEY'))}

            try:
                r = requests.get(self.url, headers=headers_dict)
                response = r.json()

                if response['status']:
                    obj = OffStoreDelivery.objects.get(
                        transaction_reference=ref)
                    obj.status = 'PENDING'
                    obj.amount_paid = float(
                        response['data']['amount']) / 100
                    obj.save()

                    user = get_user_data(obj.business_id)
                    from_whatsapp_number = 'whatsapp:+14155238886'
                    to_numbers = ['+2347056918098', '+2348136800327', '+2349077499434']
                    client = Client()
                    body = f"""NEW ORDER\nMerchant name: {user['firstname']} {user['lastname']}\nBusiness name: {user['businessname']}\nMerchant phone number: {user['phone']}\nPickup city: {obj.pickup_state}\nPickup address: {obj.pickup_address}\nPickup date: {obj.pickup_time}\nDestination city: {obj.destination_state}\nDestination address: {obj.destination_address}\nReceiver's name: {obj.customer_name}\nReceiver's phone number: {obj.customer_phone}\nNo of items to be shipped: {obj.number_of_items}\nAmount paid: {obj.amount_paid}\nShipping type: {obj.shipping_type}
                            """
                    for number in to_numbers:
                        client.messages.create(to=f'whatsapp:{number}', from_=from_whatsapp_number, body=body)

                    if response['data']['status'] == 'success':
                        return Response({'success': True}, status=status.HTTP_200_OK)

                    return Response({'success': False}, status=status.HTTP_200_OK)

                return Response({'success': False, 'errors': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'error': 'no ref'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
