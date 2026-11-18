# QuickBasket - E-commerce web app built with Django

[![CI](https://github.com/Manish12858/quickbasket/actions/workflows/ci.yml/badge.svg)](https://github.com/Manish12858/quickbasket/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)

QuickBasket is a small online store I built while learning Django. You can browse and search
products, add them to a cart, sign up with email verification and place an order. Admins manage
products and orders from the Django admin.

The first version only had a product list, a cart and a very basic checkout. After that I kept
working on it: fixed the bugs I found, moved the secrets out of the code, added order history and
stock handling, and wrote tests.

| Home | Product |
|------|---------|
| ![Home page](docs/screenshots/1-home.png) | ![Product page](docs/screenshots/2-product.png) |
| **Cart** | **Checkout** |
| ![Cart](docs/screenshots/3-cart.png) | ![Checkout](docs/screenshots/4-checkout.png) |

## Features

- Product list with search, and a page for each product (`/wireless-mouse`)
- Cart stored in the session, so it works without logging in and is kept after you log in
- Add, update and remove cart items with AJAX (jQuery), the cart count updates without reloading
- "Buy now" button and stock checks, you can't add more than what is in stock
- Sign up with email verification, login, logout, profile and password reset
- Checkout with a saved shipping address (cash on delivery for now)
- "My orders" page with order details
- Django admin for products, orders and addresses

## How the checkout works

When you place an order, everything happens inside one database transaction. For each item in
the cart the product row is locked, the stock is checked and reduced, and an `OrderItem` is
saved with the price at that moment. If any product has run out, the whole order is rolled back,
so stock never goes negative and you don't get half an order. The shipping address is copied onto
the order, so changing your address later doesn't change old orders.

## Tech stack

Python 3.12, Django 6.0, SQLite, Django templates with Tailwind CSS, jQuery for the AJAX parts,
pytest and Playwright for tests, GitHub Actions for CI.

## How to run it

```bash
git clone https://github.com/Manish12858/quickbasket.git
cd quickbasket

python -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py loaddata sample_products
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000. The admin is at http://127.0.0.1:8000/admin.

You don't need to set up email. Without Gmail settings, the verification and password reset
emails are printed in the terminal, so you can copy the link from there. To send real emails,
copy `.env.example` to `.env` and fill in a Gmail address and app password.

## Tests

```bash
pip install -r requirements-dev.txt
python -m playwright install chromium

pytest                   # all tests
pytest -m "not e2e"      # skip the browser test
pytest -m e2e --headed   # watch the browser test
```

There are 44 pytest tests for the products, cart, orders and accounts, and one Playwright test
that goes through the whole flow: register, verify the email, log in, add to cart, check out.
GitHub Actions runs them on every push, and the screenshots above come from that test.

## Bugs I fixed along the way

- Saving the shipping address a second time created a duplicate instead of updating it
- Checkout crashed if you weren't logged in, and an empty cart could still be "ordered"
- The cart count was wrong after adding the same product twice
- A wrong product URL or an old verification link gave a server error instead of a 404 / message
- The email password and secret key were hard-coded in `settings.py`, now they come from environment variables

## What I learned

- How Django sessions work, and storing the cart in the session instead of the database
- Email verification links with Django's token generator
- Using `transaction.atomic()` and `select_for_update()` so two orders can't buy the same last item
- Why money should be a `DecimalField`
- Keeping secrets out of git with environment variables
- Writing tests with pytest-django, a browser test with Playwright, and running them in GitHub Actions

## Next steps

- Online payment with Razorpay (test mode)
- Product categories and filters
- Deploy it online

## Author

Manish Kumar | [GitHub](https://github.com/Manish12858) | manishkumarjamia@gmail.com

Sample product images are illustrations made for this project.
