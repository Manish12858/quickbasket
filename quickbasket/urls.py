"""URL configuration for the QuickBasket project."""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('users/', include('users.urls')),
    path('orders/', include('orders.urls')),
]

# Serve uploaded product images from Django. Fine for development and small demo deployments;
# a production setup would serve /media/ from a web server or object storage instead.
if settings.SERVE_MEDIA:
    media_prefix = settings.MEDIA_URL.lstrip('/')
    urlpatterns += [re_path(rf'^{media_prefix}(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
