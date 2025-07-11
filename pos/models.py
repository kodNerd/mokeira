from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User

# Create your models here.

class Stock(models.Model):
    product_name = models.CharField(max_length=100)
    product_type = models.CharField(max_length=100, blank=True, null=True)
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    expiry_date = models.DateField(blank=True, null=True)
    supplier = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"

class Sale(models.Model):
    product = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return float(getattr(self, 'quantity', 0) or 0) * float(getattr(self, 'selling_price', 0) or 0)

    def __str__(self):
        product = getattr(self, 'product', None)
        sale_date = getattr(self, 'sale_date', None)
        product_name = getattr(product, 'product_name', 'Unknown') if product else 'Unknown'
        date_str = sale_date.date() if sale_date else 'Unknown'
        return f"{product_name} - {self.quantity} sold on {date_str}"

class Expense(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    staff = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.description} - {self.amount} on {self.date}"

class Injection(models.Model):
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    staff = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.description} - {self.amount} on {self.date}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150)
    shop_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, unique=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
