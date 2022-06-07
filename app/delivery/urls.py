from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


app_name = 'delivery'

router = DefaultRouter()
router.register('delivery', OffStoreDeliveryViewSet)

urlpatterns = [
    path('verify-transaction/', VerifyTransaction.as_view(), name='verify-transaction'),
]
