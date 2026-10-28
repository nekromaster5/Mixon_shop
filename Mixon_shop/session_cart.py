# Mixon_shop/session_cart.py
from decimal import Decimal

from django.conf import settings

from Mixon_shop.models import Product


class SessionCart:
    """Единая реализация корзины на сессии — используется и гостями, и авторизованными
    пользователями. Формат в сессии: {'<product_id>': {'quantity': int, 'price': '123.45'}}.
    Цена в сессии — на момент добавления; при показе и в сумме берётся актуальная цена товара
    (с учётом скидки), поэтому изменение цены или скидки в админке сразу попадает в корзину.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False):
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.current_price)}
        if update_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        self.save()

    def set_quantity(self, product, quantity):
        """Выставить точное количество товара. quantity <= 0 удаляет товар из корзины."""
        if quantity <= 0:
            self.remove(product)
            return
        self.add(product, quantity=quantity, update_quantity=True)

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids).prefetch_related('images')
        products_by_id = {str(product.id): product for product in products}

        for product_id, item in list(self.cart.items()):
            product = products_by_id.get(product_id)
            if product is None:
                # Товар удалили из каталога — не показываем его в корзине.
                continue
            item = dict(item)
            item['product'] = product
            item['price'] = product.current_price
            item['total_price'] = product.current_price * item['quantity']
            yield item

    def __len__(self):
        return self.get_total_quantity()

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        return sum((item['total_price'] for item in self), Decimal('0'))

    def clear(self):
        if settings.CART_SESSION_ID in self.session:
            del self.session[settings.CART_SESSION_ID]
            self.save()

    def save(self):
        self.session.modified = True
