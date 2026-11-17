import os

import pytest
from django.core.management import call_command

# Playwright's sync API runs an event loop in the test thread; allow Django ORM calls there.
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

PASSWORD = "Str0ng-pass-123"


@pytest.fixture
def products(db):
    """The 6 sample products from products/fixtures/sample_products.json, keyed by slug."""
    from products.models import Product

    call_command("loaddata", "sample_products", verbosity=0)
    return {product.slug: product for product in Product.objects.all()}


@pytest.fixture
def user(db, django_user_model):
    return django_user_model.objects.create_user(username="asha", email="asha@example.com", password=PASSWORD)


@pytest.fixture
def other_user(db, django_user_model):
    return django_user_model.objects.create_user(username="ravi", email="ravi@example.com", password=PASSWORD)


@pytest.fixture
def logged_in_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def address(user):
    from orders.models import Address

    return Address.objects.create(
        user=user,
        full_name="Asha Verma",
        phone="9876543210",
        line1="12 MG Road",
        city="Pune",
        state="Maharashtra",
        postal_code="411001",
        country="India",
    )


@pytest.fixture
def add_to_cart(client):
    """Helper: add_to_cart(product, qty) using the AJAX endpoint."""
    from django.urls import reverse

    def _add(product, qty=1, using=None):
        return (using or client).post(reverse("cart_add"), {"product_id": product.id, "product_quantity": qty})

    return _add
