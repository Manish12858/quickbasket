from django.urls import reverse

from products.models import Product


def test_slug_is_generated_and_kept_unique(db):
    first = Product.objects.create(name="Desk Lamp", price="999.00", description="LED lamp", image="samples/x.jpg", stock=5)
    second = Product.objects.create(name="Desk Lamp", price="799.00", description="LED lamp", image="samples/x.jpg", stock=5)
    assert first.slug == "desk-lamp"
    assert second.slug == "desk-lamp-1"


def test_new_products_are_active_by_default(db):
    product = Product.objects.create(name="Mouse Pad", price="299.00", description="Pad", image="samples/x.jpg", stock=1)
    assert product.active is True


def test_index_lists_only_active_products(client, products):
    hidden = products["wireless-mouse"]
    hidden.active = False
    hidden.save()

    response = client.get(reverse("index"))

    assert response.status_code == 200
    assert "Full-Size Mechanical Keyboard" in response.text
    assert "Wireless Mouse" not in response.text
    assert len(response.context["products"]) == 5


def test_search_matches_name_and_description(client, products):
    response = client.get(reverse("index"), {"q": "keyboard"})
    names = {product.name for product in response.context["products"]}
    # "keyboard" appears in two product names and in the keycap set's description
    assert names == {"Full-Size Mechanical Keyboard", "Compact 75% Mechanical Keyboard", "Linear Switch Pack (35 pcs)", "PBT Keycap Set"}


def test_search_with_no_results_shows_message(client, products):
    response = client.get(reverse("index"), {"q": "television"})
    assert len(response.context["products"]) == 0
    assert "No products found" in response.text


def test_detail_page_shows_price_and_quantity_options(client, products):
    product = products["over-ear-headphones"]  # stock 3
    response = client.get(product.get_absolute_url())
    assert response.status_code == 200
    assert "₹2,499.00" in response.text
    assert list(response.context["qty_range"]) == [1, 2, 3]
    assert "only 3 left" in response.text


def test_out_of_stock_product_cannot_be_added(client, products):
    response = client.get(products["pbt-keycap-set"].get_absolute_url())
    assert "Out of stock" in response.text
    assert 'id="add-to-cart"' not in response.text


def test_unknown_product_returns_404(client, db):
    assert client.get("/does-not-exist").status_code == 404
