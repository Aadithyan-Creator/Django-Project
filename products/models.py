from django.db import models
from django.utils import timezone


class Product(models.Model):
    CATEGORIES = [
        ('electronics', 'Electronics'),
        ('clothes', 'Clothes'),
        ('grocery', 'Grocery')
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def reduce_stock(self, quantity):
        if self.stock >= quantity:
            self.stock -= quantity
            self.save()
            return True
        return False

    def __str__(self):
        return self.name
