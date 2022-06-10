from django.db import models
import uuid


class OffStoreDelivery(models.Model):
    WEIGHT_CHOICES = [
        ('0.5kg - 4kg', '0.5kg - 4kg'),
        ('4kg - 10kg', '4kg - 10kg'),
        ('10kg - 15kg', '10kg - 15kg'),
        ('15kg - 20kg', '15kg - 20kg'),
        ('20kg - 25kg', '20kg - 25kg'),
        ('25kg - 30kg', '25kg - 30kg'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    destination_address = models.CharField(max_length=225, blank=True, null=True)
    destination_state = models.CharField(max_length=225, blank=True, null=True)
    pickup_address = models.CharField(max_length=225, blank=True, null=True)
    pickup_state = models.CharField(max_length=225, blank=True, null=True)
    average_weight = models.CharField(max_length=15, choices=WEIGHT_CHOICES, null=True, blank=True)
    business_id = models.UUIDField(blank=True, null=True)
    customer_name = models.CharField(max_length=225, blank=True, null=True)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=14, blank=True, null=True)
    number_of_items = models.IntegerField(blank=True, null=True)
    amount_paid =  models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    transaction_reference = models.CharField(max_length=225, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.company_id
