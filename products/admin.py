from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'active')
    list_editable = ('price', 'stock', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'description')
    readonly_fields = ('slug',)
