from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.crypto import get_random_string
import uuid

from numpy import maximum


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
    delivery_type = models.CharField(max_length=10, default='offstore')
    destination_address = models.CharField(max_length=225)
    destination_state = models.CharField(max_length=225)
    pickup_address = models.CharField(max_length=225)
    pickup_state = models.CharField(max_length=225)
    total_weight = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
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
    delivery_date = models.CharField(max_length=225, blank=True, null=True)
    pickup_time = models.DateField(blank=True, null=True)
    dispatched_at = models.DateTimeField(blank=True, null=True)
    intransit_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    order_placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_placed_at']

    def __str__(self):
        return str(self.business_id)

class APIDelivery(models.Model):
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
    delivery_type = models.CharField(max_length=10, default='api')
    destination_address = models.CharField(max_length=225)
    destination_address_postal_code = models.CharField(max_length=225)
    destination_state = models.CharField(max_length=225)
    pickup_address = models.CharField(max_length=225)
    pick_up_address_postal_code = models.CharField(max_length=225)
    pickup_state = models.CharField(max_length=225)
    total_weight = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    business_id = models.UUIDField(blank=True, null=True)
    logistics_company_code = models.CharField(max_length=3, null=True, blank=True)
    merchant_name = models.CharField(max_length=225, null=True, blank=True)
    merchant_number = models.CharField(max_length=14, null=True, blank=True)
    customer_name = models.CharField(max_length=225)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=14, blank=True, null=True)
    number_of_items = models.IntegerField(blank=True, null=True)
    additional_notes = models.CharField(max_length=225, blank=True, null=True)
    amount_paid =  models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True, default='AWAITING PAYMENT')
    shipping_type = models.CharField(max_length=20, choices=SHIPPING_TYPE_CHOICES, null=True, blank=True, default='NORMAL')
    transaction_reference = models.CharField(max_length=225, blank=True, null=True, default=uuid.uuid4, unique=True)
    tracking_id = models.CharField(max_length=225, blank=True, null=True)
    delivery_date = models.CharField(max_length=225, blank=True, null=True)
    pickup_time = models.DateField(blank=True, null=True)
    dispatched_at = models.DateTimeField(blank=True, null=True)
    intransit_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    order_placed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-order_placed_at']

    def __str__(self):
        return str(self.business_id)


class DeliveryRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    states = ArrayField(models.CharField(max_length=50, null=True, blank=True), null=True, blank=True)
    mininum_fee = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    rate = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    extra_size_fee = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    

class ItemsPicked(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(APIDelivery, on_delete=models.CASCADE, null=True, blank=True)
    weight = models.DecimalField(max_digits=4, decimal_places=2)
    quantity = models.IntegerField(default=1)
    name = models.CharField(max_length=225, null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__ (self):
        return self.name

class LogisticsCompany(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=225)
    code = models.CharField(max_length=3)
    image = models.FileField(upload_to='logistics/', null=True, blank=True)
    serviceable_pickup_cities = ArrayField(models.CharField(max_length=225,null=True, blank=True), null=True, blank=True)
    serviceable_dropoff_cities = ArrayField(models.CharField(max_length=225,null=True, blank=True), null=True, blank=True)
    cities_with_most_reliable_service = ArrayField(models.CharField(max_length=225,null=True, blank=True), null=True, blank=True)
    pickup_eta = models.CharField(max_length=50, null=True, blank=True)
    delivery_eta = models.CharField(max_length=50, blank=True, null=True)
    tracking_url = models.CharField(max_length=225, null=True, blank=True)

    def __str__(self):
        return self.name

class AvailableLogisticsForOrder(models.Model):
    rate_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(APIDelivery, on_delete=models.CASCADE)
    logistics_company = models.ForeignKey(LogisticsCompany, on_delete=models.CASCADE, null=True, blank=True)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.logistics_company.name