from django.db import models
from django.utils import timezone
from products.models import Product
from django.contrib.auth.models import User
from decimal import Decimal


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def grand_total(self, coupon_data=None):
        total = sum(item.final_price(coupon_data) for item in self.items.all())
        return Decimal(total)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def final_price(self, coupon_data=None):
        total_price = self.price * self.quantity
        if coupon_data:
            if coupon_data["type"] == "percentage":
                total_price *= (1 - Decimal(coupon_data["amount"]) / 100)
            elif coupon_data["type"] == "fixed":
                total_price -= Decimal(coupon_data["amount"])
                if total_price < 0:
                    total_price = Decimal("0.0")
        return total_price
