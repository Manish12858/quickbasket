from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    slug = models.SlugField(unique=True, blank=True)
    stock = models.IntegerField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', args=[self.slug])

    @property
    def in_stock(self):
        return self.stock > 0

    def save(self, *args, **kwargs):
        # Generate a unique, URL-friendly slug: "keyboard", "keyboard-1", "keyboard-2", ...
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
