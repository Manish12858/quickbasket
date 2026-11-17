from django.shortcuts import render, get_object_or_404
from .models import Product
# Create your views here.
def index(request):
    products = Product.objects.filter(active=True)
    return render(request,'products/index.html',{'products':products})

def detail(request,slug):
    product = get_object_or_404(Product, slug=slug)
    return render(request,'products/detail.html',{'product':product})