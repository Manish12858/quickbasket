from decimal import Decimal

from django.urls import reverse

from orders.models import Address, Order
from products.models import Product


def place_order(client):
    return client.post(reverse("place-order"))


def test_checkout_requires_login(client, db):
    response = client.get(reverse("checkout"))
    assert response.status_code == 302
    assert response.url == f"{reverse('login')}?next={reverse('checkout')}"


def test_checkout_with_empty_cart_redirects_to_cart(logged_in_client):
    response = logged_in_client.get(reverse("checkout"))
    assert response.url == reverse("cart-overview")


def test_checkout_page_shows_address_and_items(logged_in_client, address, products, add_to_cart):
    add_to_cart(products["wireless-mouse"], 2, using=logged_in_client)
    response = logged_in_client.get(reverse("checkout"))
    assert response.status_code == 200
    assert "12 MG Road" in response.text
    assert "₹2,398.00" in response.text


def test_place_order_requires_login(client, products, add_to_cart):
    add_to_cart(products["wireless-mouse"], 1)
    response = place_order(client)
    assert response.status_code == 401
    assert Order.objects.count() == 0


def test_place_order_rejects_empty_cart(logged_in_client, address):
    response = place_order(logged_in_client)
    assert response.status_code == 400
    assert response.json()["error"] == "Your cart is empty."


def test_place_order_requires_address(logged_in_client, products, add_to_cart):
    add_to_cart(products["wireless-mouse"], 1, using=logged_in_client)
    response = place_order(logged_in_client)
    assert response.status_code == 400
    assert "shipping address" in response.json()["error"]


def test_place_order_creates_order_reduces_stock_and_clears_cart(logged_in_client, user, address, products, add_to_cart):
    keyboard, mouse = products["compact-75-mechanical-keyboard"], products["wireless-mouse"]
    add_to_cart(keyboard, 2, using=logged_in_client)
    add_to_cart(mouse, 1, using=logged_in_client)

    response = place_order(logged_in_client)

    assert response.status_code == 200
    order = Order.objects.get()
    assert response.json()["redirect_url"] == f"/orders/{order.id}/?placed=1"
    assert order.user == user
    assert order.total_amount == Decimal("6797.00")
    assert "12 MG Road" in order.shipping_address
    assert {(item.product.slug, item.quantity, item.price) for item in order.items.all()} == {
        ("compact-75-mechanical-keyboard", 2, Decimal("2799.00")),
        ("wireless-mouse", 1, Decimal("1199.00")),
    }
    assert Product.objects.get(pk=keyboard.pk).stock == keyboard.stock - 2
    assert Product.objects.get(pk=mouse.pk).stock == mouse.stock - 1
    assert logged_in_client.session["cart"] == {}


def test_order_is_rolled_back_when_stock_runs_out(logged_in_client, address, products, add_to_cart):
    headphones = products["over-ear-headphones"]
    add_to_cart(products["wireless-mouse"], 1, using=logged_in_client)
    add_to_cart(headphones, 3, using=logged_in_client)
    Product.objects.filter(pk=headphones.pk).update(stock=1)  # someone else bought them meanwhile

    response = place_order(logged_in_client)

    assert response.status_code == 409
    assert "Only 1 left" in response.json()["error"]
    assert Order.objects.count() == 0
    assert Product.objects.get(slug="wireless-mouse").stock == 25  # nothing was deducted


def test_saving_address_twice_updates_the_same_address(logged_in_client, user):
    data = {
        "full_name": "Asha Verma", "phone": "9876543210", "line1": "12 MG Road", "line2": "",
        "city": "Pune", "state": "Maharashtra", "postal_code": "411001", "country": "India",
    }
    logged_in_client.post(reverse("add_address"), data)
    logged_in_client.post(reverse("add_address"), {**data, "city": "Mumbai"})
    assert Address.objects.filter(user=user).count() == 1
    assert Address.objects.get(user=user).city == "Mumbai"


def test_order_pages_show_only_own_orders(logged_in_client, user, other_user):
    mine = Order.objects.create(user=user, total_amount=100)
    theirs = Order.objects.create(user=other_user, total_amount=200)

    response = logged_in_client.get(reverse("my-orders"))
    assert list(response.context["orders"]) == [mine]
    assert logged_in_client.get(reverse("order-detail", args=[mine.id])).status_code == 200
    assert logged_in_client.get(reverse("order-detail", args=[theirs.id])).status_code == 404


def test_order_detail_shows_confirmation_after_placing(logged_in_client, user):
    order = Order.objects.create(user=user, total_amount=100)
    response = logged_in_client.get(reverse("order-detail", args=[order.id]) + "?placed=1")
    assert "Thank you! Your order has been placed." in response.text
