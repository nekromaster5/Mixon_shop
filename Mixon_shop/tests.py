import json
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.test import TestCase
from django.urls import reverse
from django.utils.timezone import now

from .models import (Branch, Category, City, Order, OrderProduct, OrderStatus, PaymentMethod, Product,
                     ProductStock, PromoCode, ShipmentMethod)


class ShopTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        category = Category.objects.create(name='Фарби')
        cls.paint = Product.objects.create(name='Фарба', category=category, price=Decimal('100.00'))
        cls.primer = Product.objects.create(name='Ґрунт', category=category, price=Decimal('200.00'),
                                            discount_price=Decimal('150.00'), is_discounted=True)
        cls.branch = Branch.objects.create(city=City.objects.create(name='Одеса'), address_short='вул. Тестова, 1',
                                           map_info='-')
        cls.shipment = ShipmentMethod.objects.create(name='Самовивіз', image='shipment.png')
        cls.payment = PaymentMethod.objects.create(name='Готівка', image='payment.png')
        OrderStatus.objects.create(id=1, name='Заказ принят')


class CreateOrderTests(ShopTestCase):
    url = reverse('create_order')

    def order_data(self, **overrides):
        data = {
            'name': 'Daniil',
            'phone': '+380000000000',
            'shipment_method': self.shipment.id,
            'order_place': self.branch.id,
            'payment_method': self.payment.id,
            'goods_cost': 1,
            'shipment_cost': 50,
            'products': {str(self.paint.id): 2, str(self.primer.id): 1},
        }
        data.update(overrides)
        return data

    def post(self, data):
        return self.client.post(self.url, json.dumps(data), content_type='application/json')

    def test_creates_order_with_products(self):
        response = self.post(self.order_data())

        self.assertEqual(response.status_code, 200)
        order = Order.objects.get()
        quantities = dict(OrderProduct.objects.filter(order=order).values_list('product_id', 'quantity'))
        self.assertEqual(quantities, {self.paint.id: 2, self.primer.id: 1})

    def test_goods_cost_is_calculated_on_server(self):
        # Клиент прислал goods_cost = 1, но сервер считает сам: 2 * 100 + 1 * 150 (цена со скидкой)
        self.post(self.order_data())

        self.assertEqual(Order.objects.get().goods_cost, Decimal('350.00'))

    def test_percentage_promo_code(self):
        PromoCode.objects.create(code='SALE10', discount_type='percentage', discount_value=Decimal('10'))

        self.post(self.order_data(promo_code='SALE10'))

        order = Order.objects.get()
        self.assertTrue(order.promo_applied)
        self.assertEqual(order.goods_cost, Decimal('315.00'))

    def test_amount_promo_code_does_not_go_below_zero(self):
        PromoCode.objects.create(code='BIG', discount_type='amount', discount_value=Decimal('1000'))

        self.post(self.order_data(promo_code='BIG'))

        self.assertEqual(Order.objects.get().goods_cost, Decimal('0.00'))

    def test_unknown_product_creates_nothing(self):
        response = self.post(self.order_data(products={str(self.paint.id): 1, '999999': 1}))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.exists())

    def test_requires_phone_or_email(self):
        response = self.post(self.order_data(phone=''))

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Order.objects.exists())

    def test_rejects_non_positive_quantity(self):
        response = self.post(self.order_data(products={str(self.paint.id): 0}))

        self.assertEqual(response.status_code, 400)

    def test_rejects_invalid_json(self):
        response = self.client.post(self.url, 'not json', content_type='application/json')

        self.assertEqual(response.status_code, 400)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)


class ApplyPromoCodeTests(ShopTestCase):
    url = reverse('apply_promo_code')

    def test_valid_code_is_saved_in_session_and_counted(self):
        promo = PromoCode.objects.create(code='SALE10', discount_type='percentage', discount_value=Decimal('10'))

        response = self.client.post(self.url, {'code': 'SALE10'})

        self.assertEqual(response.json(), {'success': True, 'discount': '10.00%'})
        self.assertEqual(self.client.session['applied_promo_code'], 'SALE10')
        promo.refresh_from_db()
        self.assertEqual(promo.usage_count, 1)

    def test_expired_code(self):
        PromoCode.objects.create(code='OLD', discount_type='amount', discount_value=Decimal('10'),
                                 expiry_date=now() - timedelta(days=1))

        response = self.client.post(self.url, {'code': 'OLD'})

        self.assertEqual(response.status_code, 400)

    def test_usage_limit(self):
        PromoCode.objects.create(code='ONCE', discount_type='amount', discount_value=Decimal('10'),
                                 max_usage_count=1, usage_count=1)

        response = self.client.post(self.url, {'code': 'ONCE'})

        self.assertEqual(response.status_code, 400)

    def test_unknown_code(self):
        response = self.client.post(self.url, {'code': 'NOPE'})

        self.assertEqual(response.status_code, 400)


class SessionCartTests(ShopTestCase):
    def test_add_and_remove(self):
        self.client.get(reverse('cart_add', args=[self.paint.id]))
        self.client.get(reverse('cart_add', args=[self.paint.id]))

        cart = self.client.session[settings.CART_SESSION_ID]
        self.assertEqual(cart[str(self.paint.id)]['quantity'], 2)

        self.client.get(reverse('cart_remove', args=[self.paint.id]))

        self.assertNotIn(str(self.paint.id), self.client.session[settings.CART_SESSION_ID])

    def test_add_unknown_product_returns_404(self):
        self.assertEqual(self.client.get(reverse('cart_add', args=[999999])).status_code, 404)


class ProductStockTests(ShopTestCase):
    def test_in_stock_flag_follows_stock_records(self):
        stock = ProductStock.objects.create(product=self.paint, branch=self.branch, quantity=5)
        self.paint.refresh_from_db()
        self.assertTrue(self.paint.is_in_stock)

        stock.delete()
        self.paint.refresh_from_db()
        self.assertFalse(self.paint.is_in_stock)

    def test_str(self):
        stock = ProductStock.objects.create(product=self.paint, branch=self.branch, quantity=5)

        self.assertIn('Фарба', str(stock))
