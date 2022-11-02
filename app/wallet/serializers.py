from rest_framework import serializers
from .models import *

class EcommerceStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = EcommerceStore
        exclude = ['associated_company_id']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        wallet = Wallet.objects.get(owner__id=str(representation['id']))
        representation['account_number'] = wallet.virtual_account_number
        representation['bank'] = wallet.virtual_bank
        return representation
