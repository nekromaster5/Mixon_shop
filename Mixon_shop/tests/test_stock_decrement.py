import json

import pytest

from Mixon_shop.models import ProductStock


@pytest.mark.django_db
def test_order_decrements_stock_for_variant_less_product(
    client, make_product, branch, shipment_method, payment_method, order_status
):
    product = make_product(price="10.00")
    stock = ProductStock.objects.create(product=product, branch=branch, quantity=5)

    payload = {
        "name": "Buyer", "phone": "+380000000000", "email": "",
        "shipment_method": shipment_method.id, "order_place": branch.id,
        "payment_method": payment_method.id, "comment": "",
        "goods_cost": 20, "shipment_cost": 0,
        "products": {str(product.id): 2}, "promo_code": None,
    }
    response = client.post("/create-order/", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    assert json.loads(response.content)["success"] is True

    stock.refresh_from_db()
    assert stock.quantity == 3


@pytest.mark.django_db
def test_order_does_not_oversell_below_zero(
    client, make_product, branch, shipment_method, payment_method, order_status
):
    product = make_product(price="10.00")
    stock = ProductStock.objects.create(product=product, branch=branch, quantity=1)

    payload = {
        "name": "Buyer", "phone": "+380000000000", "email": "",
        "shipment_method": shipment_method.id, "order_place": branch.id,
        "payment_method": payment_method.id, "comment": "",
        "goods_cost": 50, "shipment_cost": 0,
        "products": {str(product.id): 5}, "promo_code": None,
    }
    client.post("/create-order/", data=json.dumps(payload), content_type="application/json")

    stock.refresh_from_db()
    assert stock.quantity == 0


@pytest.mark.django_db
def test_order_skips_decrement_for_variant_specific_stock(
    client, make_product, branch, shipment_method, payment_method, order_status
):
    """Товар со складом, у которого задан конкретный объём/цвет — покупатель
    пока нигде не выбирает вариант, поэтому автосписание для него не выполняется."""
    from Mixon_shop.models import Volume

    product = make_product(price="10.00")
    volume = Volume.objects.create(size="1.00")
    stock = ProductStock.objects.create(product=product, branch=branch, volume=volume, quantity=5)

    payload = {
        "name": "Buyer", "phone": "+380000000000", "email": "",
        "shipment_method": shipment_method.id, "order_place": branch.id,
        "payment_method": payment_method.id, "comment": "",
        "goods_cost": 10, "shipment_cost": 0,
        "products": {str(product.id): 1}, "promo_code": None,
    }
    response = client.post("/create-order/", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    assert json.loads(response.content)["success"] is True

    stock.refresh_from_db()
    assert stock.quantity == 5  # не тронуто


@pytest.mark.django_db
def test_order_without_matching_stock_row_does_not_crash(
    client, make_product, branch, shipment_method, payment_method, order_status
):
    product = make_product(price="10.00")  # ни одного ProductStock вообще

    payload = {
        "name": "Buyer", "phone": "+380000000000", "email": "",
        "shipment_method": shipment_method.id, "order_place": branch.id,
        "payment_method": payment_method.id, "comment": "",
        "goods_cost": 10, "shipment_cost": 0,
        "products": {str(product.id): 1}, "promo_code": None,
    }
    response = client.post("/create-order/", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    assert json.loads(response.content)["success"] is True
