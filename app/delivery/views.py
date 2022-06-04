from rest_framework import views, viewsets, status, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
import os, requests


class OffStoreDeliveryViewSet(viewsets.ModelViewSet):
    queryset = OffStoreDelivery
    serializer_class = OffStoreDeliverySerializer
    permission_classes = [IsAuthenticated, ]
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['customer_name', 'customer_email',
                     'customer_phone', 'destination_state', 'pickup_state']

    def get_queryset(self, request, *args, **kwargs):
        return self.queryset.filter(company_id=request.user.id)


# class VerifyTransaction(views.APIView):
#     url =  'https://api.paystack.co/transaction/verify/'
#     serializer_class = OffStoreDeliverySerializer

#     def post(self, request, *args, **kwargs):
#         ref = self.request.query_params.get('reference', None)

#         if ref is not None:
#             self.url = self.url + ref
#             headers_dict = {'Authorization': "Bearer {}".format(os.environ.get('PAYSTACK_SECRET_KEY'))}

#             try:
#                 r = requests.get(self.url, headers=headers_dict)
#                 response = r.json()

#                 if response['status']:
#                     if seriaizer.is_validl():
#                         store_id = request.data['vendor']
#                         wallet = Wallet.objects.get(store_owner__id=store_id)
                        
#                         if Order.objects.filter(paystack_reference=ref).count() < 1:
#                             wallet.available_funds += request.data['paid_amount']
#                             wallet.save()
#                             serializer.save()
#                         else:
#                             return Response({'success':False, 'errors': "Order exists and previously paid for"}, status=status.HTTP_400_BAD_REQUEST)
#                     else:
#                         return Response({'success':False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#                     if response['data']['status'] == 'success':
#                         return Response({'success':True}, status=status.HTTP_200_OK)

#                     return Response({'success':True}, status=status.HTTP_200_OK)

#                 return Response({'success':False, 'errors':'Payment Failed'}, status=status.HTTP_400_BAD_REQUEST)
                
#             except Exception as e:
#                 capture_exception(e)
#                 return Response({'success':False, 'errors':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         return Response({'success':False, 'error': 'no ref'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    
