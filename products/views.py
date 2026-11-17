from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from cart.cart import MAX_QTY_PER_ITEM
from .models import Product


def index(request):
    query = request.GET.get('q', '').strip()
    products = Product.objects.filter(active=True).order_by('name')
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    return render(request, 'products/index.html', {'products': products, 'query': query})


def detail(request, slug):
    product = get_object_or_404(Product, slug=slug, active=True)
    max_qty = min(product.stock, MAX_QTY_PER_ITEM)
    return render(request, 'products/detail.html', {
        'product': product,
        'qty_range': range(1, max_qty + 1),
    })
