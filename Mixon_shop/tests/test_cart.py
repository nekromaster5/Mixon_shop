import json

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
    assert "Ваша корзина пуста" in response.content.decode()
