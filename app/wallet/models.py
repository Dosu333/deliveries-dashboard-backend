from django.db import models
import uuid


class EcommerceStore(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    business_name = models.CharField(max_length=225, blank=True, null=True)
    merchant_firstname = models.CharField(max_length=225, blank=True, null=True)
    merchant_lastname = models.CharField(max_length=225, blank=True, null=True)
    phone = models.CharField(max_length=14, blank=True, null=True)
    associated_company_id = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.name

class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    owner = models.OneToOneField(EcommerceStore, on_delete=models.SET_NULL, blank=True, null=True)
    balance = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, null=True, blank=True)
    credits = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, null=True, blank=True)
    account_number = models.CharField(max_length=10, null=True, blank=True)
    bank = models.CharField(max_length=255, blank=True, null=True)
    customer_code = models.CharField(max_length=255, blank=True, null=True)
    virtual_bank_account = models.CharField(max_length=10, blank=True, null=True)
    virtual_bank = models.CharField(max_length=225, blank=True, null=True)

    def __str__(self):
        return self.store_name

    def deposit(self, amount):
        self.balance = self.balance + amount
        self.save()

    def withdraw(self, amount):
        self.balance = self.balance - amount
        self.save()


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('SUCCESSFUL', 'SUCCESSFUL'),
        ('PENDING', 'PENDING'),
        ('FAILED', 'FAILED'),
        ('REVERSED', 'REVERSED')
    ]

    TRANSACTION_CHOICES = [
        ('DEPOSIT', 'DEPOSIT'),
        ('WITHDRAW', 'WITHDRAW'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    associated_wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, null=True, blank=True)
    reference = models.CharField(max_length=225, blank=True, null=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2, default=0.00, null=True, blank=True)
    transfer_code = models.CharField(max_length=225, blank=True, null=True)
    transaction_type = models.CharField(max_length=13, choices=TRANSACTION_CHOICES, null=True, blank=True, default='WITHDRAW')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, null=True, blank=True, default='PENDING')

    def __str__(self):
        return self.owner.firstname

