from django.db import models
from django.utils import timezone
from products.models import Product
from account.models import Account
from decimal import Decimal

class Cart(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='carts')
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
        price_after_discount = self.price * self.quantity
        if coupon_data:
            if coupon_data["type"] == "percentage":
                price_after_discount *= (1 - Decimal(coupon_data["amount"]) / 100)
            elif coupon_data["type"] == "fixed":
                price_after_discount -= Decimal(coupon_data["amount"])
                if price_after_discount < 0:
                    price_after_discount = Decimal("0.0")
        return price_after_discount
