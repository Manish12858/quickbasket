"""End-to-end test of the main user journey in a real browser (Playwright + Django live server).

Run:  pytest -m e2e            (headless)
      pytest -m e2e --headed   (watch the browser)
Set SCREENSHOTS_DIR=docs/screenshots to also save the README screenshots.
"""
import os
import re
from pathlib import Path

import pytest
from django.core import mail

pytest.importorskip("playwright")
from playwright.sync_api import Page, expect  # noqa: E402

from products.models import Product  # noqa: E402

pytestmark = pytest.mark.e2e

SCREENSHOTS_DIR = os.environ.get("SCREENSHOTS_DIR")
PASSWORD = "Str0ng-pass-123"


@pytest.fixture
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 1280, "height": 860}}


def screenshot(page: Page, name: str, full_page: bool = False):
    if not SCREENSHOTS_DIR:
        return
    Path(SCREENSHOTS_DIR).mkdir(parents=True, exist_ok=True)
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(Path(SCREENSHOTS_DIR) / f"{name}.png"), full_page=full_page)


def test_customer_can_register_shop_and_place_an_order(page: Page, live_server, products):
    base = live_server.url

    # Browse and search
    page.goto(base)
    expect(page.get_by_test_id("product-card")).to_have_count(6)
    screenshot(page, "1-home", full_page=True)

    page.get_by_placeholder("Search products...").fill("mouse")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_test_id("product-card")).to_have_count(1)

    # Register and verify the email address
    page.goto(f"{base}/users/register")
    page.fill("#id_username", "asha")
    page.fill("#id_email", "asha@example.com")
    page.fill("#id_password1", PASSWORD)
    page.fill("#id_password2", PASSWORD)
    page.get_by_role("button", name="Create account").click()
    expect(page.get_by_role("heading", name="Check your email")).to_be_visible()

    link = re.search(r"https?://\S+/users/email-verification/\S+", mail.outbox[-1].body).group(0)
    page.goto(link)
    expect(page.get_by_role("heading", name="Email verified")).to_be_visible()

    # Log in
    page.get_by_role("link", name="Log in").click()
    page.fill("#id_username", "asha")
    page.fill("#id_password", PASSWORD)
    page.get_by_role("button", name="Log in").click()
    expect(page.get_by_role("link", name="Hi, asha")).to_be_visible()

    # Add two products to the cart
    page.get_by_role("link", name=re.compile("Compact 75% Mechanical Keyboard")).click()
    page.select_option("#qty", "2")
    screenshot(page, "2-product")
    page.click("#add-to-cart")
    expect(page.locator("#cart-qty")).to_have_text("2")
    expect(page.locator("#cart-message")).to_contain_text("Added to cart")

    page.goto(f"{base}/wireless-mouse")
    page.click("#add-to-cart")
    expect(page.locator("#cart-qty")).to_have_text("3")

    # Cart
    page.locator('a[aria-label="Cart"]').click()
    expect(page.get_by_test_id("cart-item")).to_have_count(2)
    expect(page.locator("#total")).to_have_text("₹6,797.00")
    screenshot(page, "3-cart")

    # Checkout: add an address, then place the order
    page.get_by_role("link", name="Proceed to checkout").click()
    expect(page.locator("#place-order")).to_be_disabled()
    page.get_by_role("link", name="Add address").click()
    page.fill("#id_full_name", "Asha Verma")
    page.fill("#id_phone", "9876543210")
    page.fill("#id_line1", "12 MG Road")
    page.fill("#id_city", "Pune")
    page.fill("#id_state", "Maharashtra")
    page.fill("#id_postal_code", "411001")
    page.fill("#id_country", "India")
    page.get_by_role("button", name="Save address").click()

    expect(page.get_by_test_id("shipping-address")).to_contain_text("12 MG Road")
    screenshot(page, "4-checkout")
    page.click("#place-order")

    expect(page.get_by_test_id("order-success")).to_be_visible()
    screenshot(page, "5-order-confirmation")

    # Order history and stock
    page.get_by_role("link", name="My orders").first.click()
    expect(page.get_by_test_id("order-row")).to_have_count(1)
    expect(page.locator("#cart-qty")).to_have_text("0")
    assert Product.objects.get(slug="compact-75-mechanical-keyboard").stock == 6
    assert Product.objects.get(slug="wireless-mouse").stock == 24
