from decimal import Decimal

from products.models import Product

MAX_QTY_PER_ITEM = 10


class Cart:
    """Shopping cart stored in the user's session.

    Session format: {"<product_id>": {"price": "3499.00", "qty": 2}, ...}
    Works for guests and logged-in users without touching the database.
    """

    def __init__(self, request):
        self.session = request.session
        if 'cart' not in self.session:
            self.session['cart'] = {}
        self.cart = self.session['cart']

    def __len__(self):
        return sum(int(item['qty']) for item in self.cart.values())

    def __iter__(self):
        products = Product.objects.filter(id__in=self.cart.keys())
        products_by_id = {str(product.id): product for product in products}
        for product_id, stored in self.cart.items():
            product = products_by_id.get(product_id)
            if product is None:
                continue  # product was deleted after it was added to the cart
            price = Decimal(stored['price'])
            qty = int(stored['qty'])
            yield {
                'product': product,
                'price': price,
                'qty': qty,
                'total': price * qty,
                'max_qty': min(product.stock, MAX_QTY_PER_ITEM),
            }

    def get_quantity(self, product_id):
        item = self.cart.get(str(product_id))
        return int(item['qty']) if item else 0

    def get_total_price(self):
        return sum((Decimal(item['price']) * int(item['qty']) for item in self.cart.values()), Decimal('0'))

    def add(self, product, product_qty):
        """Set the quantity of a product (adds the product if it is not in the cart yet)."""
        product_id = str(product.id)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = int(product_qty)
        else:
            self.cart[product_id] = {'price': str(product.price), 'qty': int(product_qty)}
        self.session.modified = True

    def update(self, product, qty):
        product_id = str(product)
        if product_id in self.cart:
            self.cart[product_id]['qty'] = int(qty)
        self.session.modified = True

    def delete(self, product_id):
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
        self.session.modified = True

    def clear(self):
        self.session['cart'] = {}
        self.cart = self.session['cart']
        self.session.modified = True
