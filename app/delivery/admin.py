from django.contrib import admin
from .models import *

class OffstoreDeliveryAdmin(admin.ModelAdmin):
    list_filter = ['status', ]
    date_hierarchy = 'order_placed_at'
    ordering = ['-order_placed_at']

admin.site.register(OffStoreDelivery, OffstoreDeliveryAdmin)
admin.site.register(DeliveryRate)
