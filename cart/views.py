from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from products.models import Product
from .cart import Cart, MAX_QTY_PER_ITEM


def _positive_int(value):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _get_product(request):
    product_id = _positive_int(request.POST.get('product_id'))
    if product_id is None:
        return None
    return Product.objects.filter(id=product_id, active=True).first()


def _cart_summary(cart):
    return {'qty': len(cart), 'total': str(cart.get_total_price())}


@require_POST
def cart_add(request):
    cart = Cart(request)
    product = _get_product(request)
    if product is None:
        return JsonResponse({'error': 'Product not found.'}, status=404)
    qty = _positive_int(request.POST.get('product_quantity'))
    if qty is None:
        return JsonResponse({'error': 'Please choose a valid quantity.'}, status=400)

    new_qty = cart.get_quantity(product.id) + qty
    limit = min(product.stock, MAX_QTY_PER_ITEM)
    if new_qty > limit:
        if product.stock == 0:
            message = 'Sorry, this product is out of stock.'
        else:
            message = f'You can buy up to {limit} of this product.'
        return JsonResponse({'error': message}, status=400)

    cart.add(product=product, product_qty=new_qty)
    return JsonResponse(_cart_summary(cart))


@require_POST
def cart_update(request):
    cart = Cart(request)
    product = _get_product(request)
    qty = _positive_int(request.POST.get('product_quantity'))
    if product is None or cart.get_quantity(product.id) == 0:
        return JsonResponse({'error': 'This product is not in your cart.'}, status=404)
    if qty is None or qty > min(product.stock, MAX_QTY_PER_ITEM):
        return JsonResponse({'error': 'Please choose a valid quantity.'}, status=400)
    cart.update(product=product.id, qty=qty)
    return JsonResponse(_cart_summary(cart))


@require_POST
def cart_delete(request):
    cart = Cart(request)
    cart.delete(product_id=request.POST.get('product_id'))
    return JsonResponse(_cart_summary(cart))


def cart_overview(request):
    return render(request, 'cart/cart-overview.html', {
        'cart': Cart(request),
        'qty_choices': range(1, MAX_QTY_PER_ITEM + 1),
    })
