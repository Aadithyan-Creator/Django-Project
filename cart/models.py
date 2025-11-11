from django.db import models
from django.utils import timezone
from products.models import Product
from account.models import Account


class Cart(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def total_price(self):
        return sum(item.subtotal() for item in self.items.all())

    def total_discount(self):
        return sum(item.discount_amount() for item in self.items.all())

    def final_amount(self):
        return self.total_price() - self.total_discount()

    def __str__(self):
        return f"Cart #{self.pk} - {self.account.first_name}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def subtotal(self):
        return self.price * self.quantity

    def discount_amount(self):
        return (self.discount_percent / 100) * self.subtotal()

    def final_price(self):
        return self.subtotal() - self.discount_amount()


class CartCoupon(models.Model):
    class CouponChoices(models.IntegerChoices):
        TEN = 111111, '10% Discount'
        TWENTY = 222222, '20% Discount'
        THIRTY = 333333, '30% Discount'
        FORTY = 444444, '40% Discount'
        FIFTY = 555555, '50% Discount'

    coupon_code = models.IntegerField(unique=True)
    discount_type = models.IntegerField(choices=CouponChoices.choices)
    discount_active = models.BooleanField(default=True)

    def coupon_discount(self, cart):
        grand_total = cart.final_amount()
        if not self.discount_active:
            return grand_total

        label = self.CouponChoices(self.discount_type).label  # e.g. '10% Discount'
        discount_percent = int(label.split('%')[0])
        discount_amount = grand_total * discount_percent / 100

        return grand_total - discount_amount

    def __str__(self):
        status = "Active" if self.discount_active else "Inactive"
        label = self.CouponChoices(self.discount_type).label
        return f"Coupon {self.coupon_code} - {label} ({status})"
