from django.urls import reverse


def session_cart(client):
    return client.session.get("cart", {})


def test_add_to_cart_returns_new_count(client, products, add_to_cart):
    keyboard = products["compact-75-mechanical-keyboard"]
    response = add_to_cart(keyboard, 2)
    assert response.status_code == 200
    assert response.json() == {"qty": 2, "total": "5598.00"}
    assert session_cart(client)[str(keyboard.id)]["qty"] == 2


def test_adding_same_product_again_increases_quantity(client, products, add_to_cart):
    mouse = products["wireless-mouse"]
    add_to_cart(mouse, 1)
    response = add_to_cart(mouse, 2)
    assert response.json()["qty"] == 3


def test_cannot_add_more_than_stock(products, add_to_cart):
    response = add_to_cart(products["over-ear-headphones"], 4)  # only 3 in stock
    assert response.status_code == 400
    assert "up to 3" in response.json()["error"]


def test_cannot_add_out_of_stock_product(products, add_to_cart):
    response = add_to_cart(products["pbt-keycap-set"], 1)
    assert response.status_code == 400
    assert "out of stock" in response.json()["error"]


def test_invalid_product_and_quantity_are_rejected(client, products):
    url = reverse("cart_add")
    assert client.post(url, {"product_id": "abc", "product_quantity": 1}).status_code == 404
    assert client.post(url, {"product_id": 9999, "product_quantity": 1}).status_code == 404
    mouse = products["wireless-mouse"]
    assert client.post(url, {"product_id": mouse.id, "product_quantity": 0}).status_code == 400
    assert client.post(url, {"product_id": mouse.id, "product_quantity": "two"}).status_code == 400


def test_cart_endpoints_only_accept_post(client, db):
    assert client.get(reverse("cart_add")).status_code == 405
    assert client.get(reverse("cart_update")).status_code == 405
    assert client.get(reverse("cart_delete")).status_code == 405


def test_update_quantity(client, products, add_to_cart):
    mouse = products["wireless-mouse"]
    add_to_cart(mouse, 1)
    response = client.post(reverse("cart_update"), {"product_id": mouse.id, "product_quantity": 5})
    assert response.json() == {"qty": 5, "total": "5995.00"}


def test_update_rejects_quantity_above_stock(client, products, add_to_cart):
    headphones = products["over-ear-headphones"]
    add_to_cart(headphones, 1)
    response = client.post(reverse("cart_update"), {"product_id": headphones.id, "product_quantity": 5})
    assert response.status_code == 400


def test_delete_removes_product(client, products, add_to_cart):
    mouse, keyboard = products["wireless-mouse"], products["full-size-mechanical-keyboard"]
    add_to_cart(mouse, 1)
    add_to_cart(keyboard, 1)
    response = client.post(reverse("cart_delete"), {"product_id": mouse.id})
    assert response.json() == {"qty": 1, "total": "3499.00"}
    assert str(mouse.id) not in session_cart(client)


def test_cart_page_shows_items_and_total(client, products, add_to_cart):
    add_to_cart(products["compact-75-mechanical-keyboard"], 2)
    add_to_cart(products["wireless-mouse"], 1)
    response = client.get(reverse("cart-overview"))
    assert response.status_code == 200
    assert "Compact 75% Mechanical Keyboard" in response.text
    assert "₹6,797.00" in response.text


def test_empty_cart_page(client, db):
    response = client.get(reverse("cart-overview"))
    assert "Your cart is empty" in response.text


def test_cart_is_kept_after_logging_in(client, products, user, add_to_cart):
    add_to_cart(products["wireless-mouse"], 2)
    client.post(reverse("login"), {"username": "asha", "password": "Str0ng-pass-123"})
    assert session_cart(client)[str(products["wireless-mouse"].id)]["qty"] == 2
