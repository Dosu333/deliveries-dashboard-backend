from rest_framework import views, viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from user.utils import get_user_data, get_user_store_orders
from .utils import calculate_shipping_fee
from .models import *
from .serializers import *
import os
import requests


@api_view
def get_shipping_fee(request):
    if not request.data['items']:
        fee = calculate_shipping_fee(
            weight_range=request.data['weight'], merchant_state=request.data['merchant_state'], receiver_state=request.data['receiver_state'])
        return Response({'success': True, 'shipping_fee': fee['shipping_fee']}, status=status.HTTP_200_OK)


class OffStoreDeliveryViewSet(viewsets.ModelViewSet):
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


class DeliveriesView(views.APIView):
    """Get offstore and instore orders of user"""
    
    permission_classes = [IsAuthenticated, ]
    serializer_class = OffStoreDeliverySerializer

    def get(self, request, *args, **kwargs):
        try:
            offstore = OffStoreDelivery.objects.filter(
                business_id=request.user.id)
            offstore_data = self.serializer_class(offstore, many=True)
            store_orders = get_user_store_orders(request.user.id)
            return Response({'success': True, 'offstore_orders': offstore_data, 'store_orders': store_orders}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyTransaction(views.APIView):
    url = 'https://api.paystack.co/transaction/verify/'
    serializer_class = OffStoreDeliverySerializer

    def post(self, request, *args, **kwargs):
        ref = self.request.query_params.get('reference', None)
        serializer = self.serializer_class(data=request.data)

        if ref is not None:
            self.url = self.url + ref
            headers_dict = {'Authorization': "Bearer {}".format(
                os.environ.get('PAYSTACK_TEST_SECRET_KEY'))}

            try:
                r = requests.get(self.url, headers=headers_dict)
                response = r.json()

                if response['status']:
                    if serializer.is_valid():
                        if OffStoreDelivery.objects.filter(transaction_reference=ref).count() < 1:
                            serializer.save()
                        else:
                            return Response({'success': False, 'errors': "Delivery exists and previously paid for"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                    if response['data']['status'] == 'success':
                        return Response({'success': True}, status=status.HTTP_200_OK)

                    return Response({'success': False}, status=status.HTTP_200_OK)

                return Response({'success': False, 'errors': 'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'success': False, 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'success': False, 'error': 'no ref'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
