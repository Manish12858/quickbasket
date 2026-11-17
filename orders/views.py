from django.shortcuts import render,redirect
from .forms import AddressForm
from .models import Address,Order,OrderItem
from cart.cart import Cart
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def add_address(request):
    address = Address.objects.filter(user=request.user).first()
    if request.method=="POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect("checkout")
    form = AddressForm(instance=address)
    return render(request,'orders/add_address.html',{'form':form})

@login_required
def checkout(request):
    address = Address.objects.filter(user=request.user).first()
    return render(request,'orders/checkout.html',{'address':address})
    
def place_order(request):
    if request.method!="POST":
        return JsonResponse({'success':False},status=405)
    if not request.user.is_authenticated:
        return JsonResponse({'success':False,'error':'Please log in to place an order.'},status=401)
    cart = Cart(request)
    if len(cart)==0:
        return JsonResponse({'success':False,'error':'Your cart is empty.'},status=400)

    order = Order.objects.create(user=request.user,total_amount=cart.get_total_price())
    for item in cart:
        OrderItem.objects.create(order=order,product=item['product'],quantity=item['qty'])
    cart.clear()
    return JsonResponse({'success':True,'order_id':order.id})

def order_success(request):
    return render(request,'orders/order-success.html')

def order_failed(request):
    return render(request,'orders/order-failed.html')