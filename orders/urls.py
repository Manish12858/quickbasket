from django.urls import path

from . import views

urlpatterns = [
    path('add-address', views.add_address, name='add_address'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order', views.place_order, name='place-order'),
    path('my-orders', views.my_orders, name='my-orders'),
    path('<int:order_id>/', views.order_detail, name='order-detail'),
]
