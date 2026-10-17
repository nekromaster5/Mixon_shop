import pytest

from Mixon_shop.models import (
    Branch, Category, City, OrderStatus, PaymentMethod, Product, ProductType,
    Region, ShipmentMethod,
)


@pytest.fixture
def category(db):
    return Category.objects.create(name="Category")


@pytest.fixture
def product_type(db, category):
    product_type = ProductType.objects.create(name="Type")
    product_type.categories.add(category)
    return product_type


@pytest.fixture
def make_product(db, category, product_type):
    """Фабрика товаров: make_product(name="X", price="10.00", ...)."""

    def _make_product(name="Product", price="10.00", **kwargs):
        return Product.objects.create(
            name=name, category=category, type=product_type, price=price, **kwargs
        )

    return _make_product


@pytest.fixture
def product(make_product):
    return make_product()


@pytest.fixture
def branch(db):
    city = City.objects.create(name="City")
    return Branch.objects.create(city=city, address_short="Branch", map_info="{}")


@pytest.fixture
def shipment_method(db):
    return ShipmentMethod.objects.create(name="Shipment")


@pytest.fixture
def payment_method(db):
    return PaymentMethod.objects.create(name="Payment")


@pytest.fixture
def order_status(db):
    return OrderStatus.objects.get_or_create(id=1, defaults={"name": "Заказ принят"})[0]


@pytest.fixture
def region(db):
    return Region.objects.create(name="Region")
