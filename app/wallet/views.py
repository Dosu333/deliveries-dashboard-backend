from rest_framework import views, viewsets, status
from .vba import VirtualBankAccount
from .models import *
from .serializers import *


class CreateWallet(viewsets.ModelViewSet):
    """This endpoint creates an ecommerce store, a wallet for the ecommerce store and a virtual account number for the wallet"""
    queryset = EcommerceStore.objects.all()
    serializer_class = EcommerceStoreSerializer
    http_method_names = ['post']

    def perform_create(self, serializer):
        instance = serializer.save()
        acct_no = VirtualBankAccount(instance.merchant_firstname, instance.merchant_lastname, instance.merchant_phone, instance.merchant_email).create_virtual_bank_account()
        Wallet.objects.create(owner=instance, virtual_account_number=acct_no['account_no'], virtual_bank=acct_no['bank'], virtual_bank_account_name=acct_no['account_name'], customer_code=acct_no['customer'])
