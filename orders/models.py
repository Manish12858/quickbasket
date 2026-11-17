from django.contrib.auth.models import User
from django.db import models

from products.models import Product


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'addresses'

    def __str__(self):
        return f'{self.full_name}, {self.city}'

    def as_text(self):
        """Address as plain text, stored on each order as a snapshot."""
        lines = [
            self.full_name,
            self.line1,
            self.line2,
            f'{self.city}, {self.state} {self.postal_code}',
            self.country,
            f'Phone: {self.phone}',
        ]
        return '\n'.join(line for line in lines if line)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_paid = models.BooleanField(default=False)
    shipping_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Order #{self.id} by {self.user}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.quantity} × {self.product}'

    @property
    def total_price(self):
        return self.price * self.quantity
