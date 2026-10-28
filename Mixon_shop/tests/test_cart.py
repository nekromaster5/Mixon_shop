import json
from decimal import Decimal

import pytest

from Mixon_shop.models import Order


@pytest.mark.django_db
def test_add_to_cart_and_view(client, make_product):
    p1 = make_product(name="Product 1", price="100.00")
    p2 = make_product(name="Product 2", price="50.00")

    client.post(f"/cart/add/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    client.post(f"/cart/add/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")  # qty -> 2
    client.post(f"/cart/add/{p2.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    response = client.get("/cart/")
    assert response.status_code == 200
    text = response.content.decode()
    assert p1.name in text
    assert p2.name in text
    assert "250" in text  # 2x100 + 1x50


@pytest.mark.django_db
def test_cart_uses_discount_price_and_follows_price_changes(client, make_product):
    """Регрессия: корзина считала полную цену, хотя на карточке показывалась скидка."""
    discounted = make_product(name="Sale", price="100.00", discount_price="80.00", is_discounted=True)
    inactive = make_product(name="Inactive", price="50.00", discount_price="10.00", is_discounted=False)

    for product in (discounted, inactive):
        client.post(f"/cart/add/{product.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    response = client.get("/cart/")
    assert response.context["total_price"] == Decimal("130.00")  # 80 + 50, не 100 + 50

    # Цену изменили в админке после добавления в корзину — в корзине актуальная.
    discounted.discount_price = Decimal("70.00")
    discounted.save()
    response = client.get("/cart/")
    assert response.context["total_price"] == Decimal("120.00")


@pytest.mark.django_db
def test_checkout_reflects_real_cart_not_hardcoded_ids(client, make_product):
    """Регрессия: CheckoutPage раньше жёстко показывал Product.objects.filter(id__in=[1, 2])."""
    p1 = make_product(name="Product 1", price="100.00")

    client.post(f"/cart/add/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    client.post(f"/cart/add/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    response = client.get("/checkout/")
    assert response.status_code == 200
    text = response.content.decode()
    assert p1.name in text
    assert 'value="2"' in text  # количество из корзины, не захардкоженная 1


@pytest.mark.django_db
def test_cart_update_syncs_quantity_into_checkout(client, make_product):
    p1 = make_product(price="10.00")
    client.post(f"/cart/add/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    response = client.post(
        f"/cart/update/{p1.id}/", data={"quantity": "5"}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200

    response = client.get("/checkout/")
    assert 'value="5"' in response.content.decode()


@pytest.mark.django_db
def test_cart_remove(client, make_product):
    p1 = make_product()
    client.post(f"/cart/add/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    response = client.post(f"/cart/remove/{p1.id}/")
    assert response.status_code == 302

    response = client.get("/checkout/")
    assert p1.name not in response.content.decode()


@pytest.mark.django_db
def test_create_order_failure_does_not_leak_exception_text(client, make_product):
    """Регрессия: except Exception as e: return {"error": str(e)} отдавало
    клиенту сырой текст исключения (например путь к файлу, имя поля и т.п.)."""
    payload = {
        "name": "Buyer", "phone": "+380000000000", "email": "",
        "shipment_method": 999999,  # несуществующий id -> DoesNotExist внутри view
        "order_place": 999999,
        "payment_method": 999999,
        "comment": "", "goods_cost": 10, "shipment_cost": 0,
        "products": {str(make_product().id): 1}, "promo_code": None,
    }
    response = client.post("/create-order/", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 500
    body = json.loads(response.content)
    assert body["success"] is False
    assert "DoesNotExist" not in body["error"]
    assert "matching query" not in body["error"]


@pytest.mark.django_db
def test_create_order_clears_cart(client, make_product, branch, shipment_method, payment_method, order_status):
    p1 = make_product(name="Product 1", price="100.00")
    p2 = make_product(name="Product 2", price="50.00")
    client.post(f"/cart/add/{p1.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    client.post(f"/cart/add/{p2.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    payload = {
        "name": "Test Buyer",
        "phone": "+380000000000",
        "email": "",
        "shipment_method": shipment_method.id,
        "order_place": branch.id,
        "payment_method": payment_method.id,
        "comment": "",
        "goods_cost": 150,
        "shipment_cost": 0,
        "products": {str(p1.id): 1, str(p2.id): 1},
        "promo_code": None,
    }
    response = client.post("/create-order/", data=json.dumps(payload), content_type="application/json")
    assert response.status_code == 200
    body = json.loads(response.content)
    assert body["success"] is True

    order = Order.objects.get(name="Test Buyer")
    assert order.products.count() == 2

    response = client.get("/cart/")
    assert "Ваш кошик порожній" in response.content.decode()


@pytest.mark.django_db
def test_cart_keeps_selected_variants_as_separate_lines(client, make_product):
    from Mixon_shop.models import ProductParameter, ProductParameterValue, ProductTableRow

    product = make_product(name="Paint", price="100.00")
    product.parameter = ProductParameter.objects.create(name="Упаковка", unit="л")
    product.save()
    five = ProductParameterValue.objects.create(product=product, value="5")
    white = ProductTableRow.objects.create(product=product, vendor_code="W1", name="Белый")
    black = ProductTableRow.objects.create(product=product, vendor_code="B1", name="Чёрный")

    # Несколько строк таблицы сразу, у каждой своё количество
    response = client.post(
        f"/cart/add/{product.id}/",
        {"parameter_value": five.id, "row": [white.id, black.id],
         f"quantity_{white.id}": 2, f"quantity_{black.id}": 3},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.json()["success"] is True
    client.post(f"/cart/add/{product.id}/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")  # без варианта

    response = client.get("/cart/")
    items = response.context["cart_items"]
    assert [item["quantity"] for item in items] == [2, 3, 1]
    assert "Упаковка: 5 л" in items[0]["variant"] and "W1" in items[0]["variant"]
    assert response.context["total_price"] == Decimal("600.00")

    # Одну строку можно удалить, остальные остаются
    client.post(f"/cart/remove/{items[0]['key']}/")
    assert len(client.get("/cart/").context["cart_items"]) == 2


@pytest.mark.django_db
def test_cart_rejects_foreign_variant(client, make_product):
    from Mixon_shop.models import ProductTableRow

    product = make_product(name="Paint")
    other = make_product(name="Other")
    foreign = ProductTableRow.objects.create(product=other, name="Чужой")

    response = client.post(f"/cart/add/{product.id}/", {"row": foreign.id}, HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    assert response.status_code == 400
    assert len(client.get("/cart/").context["cart_items"]) == 0


@pytest.mark.django_db
def test_order_stores_variant_lines(client, make_product, branch, shipment_method, payment_method, order_status):
    from Mixon_shop.models import OrderProduct, ProductTableRow

    product = make_product(name="Paint", price="10.00")
    white = ProductTableRow.objects.create(product=product, vendor_code="W1", name="Белый")
    black = ProductTableRow.objects.create(product=product, vendor_code="B1", name="Чёрный")

    response = client.post("/create-order/", json.dumps({
        "name": "Test", "phone": "+380671234567", "shipment_method": shipment_method.id,
        "order_place": branch.id, "payment_method": payment_method.id, "goods_cost": 50, "shipment_cost": 0,
        "products": {f"{product.id}-r{white.id}": 2, f"{product.id}-r{black.id}": 3},
    }), content_type="application/json")

    assert response.status_code == 200, response.content
    lines = OrderProduct.objects.order_by("id")
    assert [(line.quantity, line.table_row) for line in lines] == [(2, white), (3, black)]
    assert "W1" in lines[0].variant
