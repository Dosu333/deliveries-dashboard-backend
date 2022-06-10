from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


app_name = 'delivery'

router = DefaultRouter()
router.register('offstore', OffStoreDeliveryViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('verify-transaction/', VerifyTransaction.as_view(), name='verify-transaction'),
    path('total-deliveries/', DeliveriesView.as_view(), name='deliveries'),
]
