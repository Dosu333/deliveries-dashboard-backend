from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.crypto import get_random_string
import uuid


class OffStoreDelivery(models.Model):
    SHIPPING_TYPE_CHOICES = [
        ('EXPRESS', 'EXPRESS'),
        ('NORMAL', 'NORMAL'),
    ]

    STATUS_CHOICES = [
        ('AWAITING PAYMENT', 'AWAITING PAYMENT'),
        ('PENDING', 'PENDING'),
        ('PICKED_UP', 'PICKED_UP'),
        ('IN_TRANSIT', 'IN_TRANSIT'),
        ('COMPLETED', 'COMPLETED')
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    destination_address = models.CharField(max_length=225)
    destination_state = models.CharField(max_length=225)
    pickup_address = models.CharField(max_length=225)
    pickup_state = models.CharField(max_length=225)
    total_weight = models.DecimalField(max_digits=4, decimal_places=1)
    business_id = models.UUIDField(blank=True, null=True)
    customer_name = models.CharField(max_length=225)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=14, blank=True, null=True)
    number_of_items = models.IntegerField(blank=True, null=True)
    additional_notes = models.CharField(max_length=225, blank=True, null=True)
    amount_paid =  models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True, default='AWAITING PAYMENT')
    shipping_type = models.CharField(max_length=20, choices=SHIPPING_TYPE_CHOICES, null=True, blank=True, default='NORMAL')
    transaction_reference = models.CharField(max_length=225, blank=True, null=True, default=uuid.uuid4, unique=True)
    pickup_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return str(self.business_id)

class DeliveryRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    states = ArrayField(models.CharField(max_length=50, null=True, blank=True))
    interstate_small_size_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    intrastate_small_size_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    intrastate_large_size_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    interstate_large_size_rate = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    min_interstate_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    max_interstate_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    min_intrastate_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    max_intrastate_fee = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    