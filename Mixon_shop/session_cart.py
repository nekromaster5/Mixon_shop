import re
from decimal import Decimal

from django.conf import settings
from django.utils.translation import gettext

from Mixon_shop.models import Product, ProductParameterValue, ProductTableRow

# Ключ строки корзины: «12» — товар без вариантов, «12-v3» — со значением параметра,
# «12-v3-r7» / «12-r7» — ещё и со строкой таблицы (например, цветом).
CART_KEY_RE = re.compile(r'^(?P<product>\d+)(?:-v(?P<value>\d+))?(?:-r(?P<row>\d+))?$')


def make_cart_key(product_id, parameter_value_id=None, table_row_id=None):
    key = str(product_id)
    if parameter_value_id:
        key += f'-v{parameter_value_id}'
    if table_row_id:
        key += f'-r{table_row_id}'
    return key


def parse_cart_key(key):
    """'12-v3-r7' -> (12, 3, 7); неверный ключ -> None."""
    match = CART_KEY_RE.match(str(key))
    if not match:
        return None
    return tuple(int(part) if part else None for part in match.group('product', 'value', 'row'))


class SessionCart:
    """Единая реализация корзины на сессии — используется и гостями, и авторизованными
    пользователями. Формат в сессии: {'<ключ>': {'quantity': int, 'price': '123.45'}}, ключ —
    см. make_cart_key: один товар может лежать несколькими строками (разные упаковки и цвета).
    Цена в сессии — на момент добавления; при показе и в сумме берётся актуальная цена товара
    (с учётом скидки), поэтому изменение цены или скидки в админке сразу попадает в корзину.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, update_quantity=False, parameter_value=None, table_row=None):
        key = make_cart_key(product.id, getattr(parameter_value, 'id', None), getattr(table_row, 'id', None))
        if key not in self.cart:
            self.cart[key] = {'quantity': 0, 'price': str(product.current_price)}
        if update_quantity:
            self.cart[key]['quantity'] = quantity
        else:
            self.cart[key]['quantity'] += quantity
        self.save()

    def set_quantity(self, key, quantity):
        """Выставить точное количество строки корзины. quantity <= 0 удаляет её."""
        key = str(key)
        if key not in self.cart:
            return
        if quantity <= 0:
            self.remove(key)
            return
        self.cart[key]['quantity'] = quantity
        self.save()

    def remove(self, key):
        key = str(key)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def __iter__(self):
        parsed = {key: parse_cart_key(key) for key in self.cart}
        parsed = {key: ids for key, ids in parsed.items() if ids}
        products = (Product.objects.filter(id__in={ids[0] for ids in parsed.values()})
                    .select_related('parameter').prefetch_related('images'))
        products_by_id = {product.id: product for product in products}
        values = ProductParameterValue.objects.filter(
            id__in={ids[1] for ids in parsed.values() if ids[1]}).select_related('product__parameter')
        values_by_id = {value.id: value for value in values}
        rows = ProductTableRow.objects.filter(id__in={ids[2] for ids in parsed.values() if ids[2]})
        rows_by_id = {row.id: row for row in rows}

        for key, item in list(self.cart.items()):
            ids = parsed.get(key)
            product = products_by_id.get(ids[0]) if ids else None
            if product is None:
                # Товар удалили из каталога — не показываем его в корзине.
                continue
            parameter_value = values_by_id.get(ids[1])
            table_row = rows_by_id.get(ids[2])
            if (ids[1] and parameter_value is None) or (ids[2] and table_row is None):
                # Вариант удалили из товара — такой строки больше не купить.
                continue
            item = dict(item)
            item['key'] = key
            item['product'] = product
            item['parameter_value'] = parameter_value
            item['table_row'] = table_row
            item['variant'] = describe_variant(product, parameter_value, table_row)
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


def describe_variant(product, parameter_value=None, table_row=None):
    """Текст варианта для корзины и заказа: «Упаковка: 5 л; Цвет: 1001 Белый»."""
    parts = []
    if parameter_value is not None:
        name = product.parameter.name if product.parameter else gettext('Упаковка')
        parts.append(f'{name}: {parameter_value.label}')
    if table_row is not None:
        parts.append(f'{product.table_title or gettext("Цвет")}: {table_row}')
    return '; '.join(parts)
