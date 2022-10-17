from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


app_name = 'wallet'

router = DefaultRouter()
router.register('create', CreateWallet)

urlpatterns = [
    path('', include(router.urls)),
]
