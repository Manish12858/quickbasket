from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from cart.cart import Cart
from products.models import Product
from .forms import AddressForm
from .models import Address, Order, OrderItem


class OutOfStock(Exception):
    pass


@login_required
def add_address(request):
    address = Address.objects.filter(user=request.user).first()
    form = AddressForm(request.POST or None, instance=address)
    if request.method == "POST" and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        address.save()
        messages.success(request, 'Shipping address saved.')
        return redirect('checkout')
    return render(request, 'orders/add_address.html', {'form': form, 'editing': address is not None})


@login_required
def checkout(request):
    if len(Cart(request)) == 0:
        messages.info(request, 'Your cart is empty.')
        return redirect('cart-overview')
    address = Address.objects.filter(user=request.user).first()
    return render(request, 'orders/checkout.html', {'address': address})


@require_POST
def place_order(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Please log in to place an order.'}, status=401)
    cart = Cart(request)
    if len(cart) == 0:
        return JsonResponse({'success': False, 'error': 'Your cart is empty.'}, status=400)
    address = Address.objects.filter(user=request.user).first()
    if address is None:
        return JsonResponse({'success': False, 'error': 'Please add a shipping address.'}, status=400)

    try:
        with transaction.atomic():
            order = Order.objects.create(user=request.user, shipping_address=address.as_text())
            total = 0
            for item in cart:
                # Lock the product row so two orders can't sell the same last item.
                product = Product.objects.select_for_update().get(pk=item['product'].pk)
                if product.stock < item['qty']:
                    raise OutOfStock(f'Only {product.stock} left of {product.name}. Please update your cart.')
                product.stock -= item['qty']
                product.save(update_fields=['stock'])
                OrderItem.objects.create(order=order, product=product, quantity=item['qty'], price=product.price)
                total += product.price * item['qty']
            order.total_amount = total
            order.save(update_fields=['total_amount'])
    except OutOfStock as error:
        return JsonResponse({'success': False, 'error': str(error)}, status=409)

    cart.clear()
    return JsonResponse({
        'success': True,
        'order_id': order.id,
        'redirect_url': reverse('order-detail', args=[order.id]) + '?placed=1',
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__product')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.prefetch_related('items__product'), id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'just_placed': request.GET.get('placed') == '1',
    })
