from Mixon_shop.models import Product

COMPARE_SESSION_ID = 'compare'
COMPARE_MAX_PRODUCTS = 4


class SessionCompare:
    """Список сравнения на сессии: работает и для гостей, и для вошедших пользователей.
    Формат в сессии: список id товаров в порядке добавления."""

    def __init__(self, request):
        self.session = request.session
        self.ids = [int(pk) for pk in self.session.get(COMPARE_SESSION_ID, [])]

    def __contains__(self, product_id):
        return int(product_id) in self.ids

    def __len__(self):
        return len(self.ids)

    def toggle(self, product):
        """Добавить товар или убрать, если уже есть. Возвращает 'added', 'removed' или 'full'."""
        if product.id in self.ids:
            self.ids.remove(product.id)
            status = 'removed'
        elif len(self.ids) >= COMPARE_MAX_PRODUCTS:
            return 'full'
        else:
            self.ids.append(product.id)
            status = 'added'
        self.save()
        return status

    def remove(self, product_id):
        if int(product_id) in self.ids:
            self.ids.remove(int(product_id))
            self.save()

    def clear(self):
        self.ids = []
        self.save()

    def save(self):
        self.session[COMPARE_SESSION_ID] = self.ids
        self.session.modified = True

    def products(self):
        """Товары в порядке добавления (удалённые из каталога пропускаются)."""
        found = {
            product.id: product
            for product in Product.objects.filter(id__in=self.ids).select_related('brand', 'category')
            .prefetch_related('images', 'characteristic_values__characteristic')
        }
        return [found[pk] for pk in self.ids if pk in found]
