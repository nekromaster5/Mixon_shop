import pytest
from django.urls import reverse

from Mixon_shop.models import Characteristic, ProductCharacteristic
from Mixon_shop.session_compare import COMPARE_MAX_PRODUCTS

AJAX = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


@pytest.mark.django_db
def test_toggle_adds_and_removes_product(client, make_product):
    product = make_product()
    url = reverse("compare_toggle", args=[product.id])

    data = client.post(url, **AJAX).json()
    assert data["status"] == "added" and data["count"] == 1

    data = client.post(url, **AJAX).json()
    assert data["status"] == "removed" and data["count"] == 0


@pytest.mark.django_db
def test_compare_limit(client, make_product):
    for i in range(COMPARE_MAX_PRODUCTS):
        client.post(reverse("compare_toggle", args=[make_product(name=f"P{i}").id]), **AJAX)
    extra = make_product(name="Extra")
    data = client.post(reverse("compare_toggle", args=[extra.id]), **AJAX).json()
    assert data["status"] == "full" and data["count"] == COMPARE_MAX_PRODUCTS


@pytest.mark.django_db
def test_toggle_requires_post(client, make_product):
    product = make_product()
    assert client.get(reverse("compare_toggle", args=[product.id])).status_code == 405


@pytest.mark.django_db
def test_compare_page_shows_characteristics_side_by_side(client, make_product):
    first, second = make_product(name="Alpha"), make_product(name="Beta")
    density = Characteristic.objects.create(name="Плотность")
    ProductCharacteristic.objects.create(product=first, characteristic=density, value="1.2")
    ProductCharacteristic.objects.create(product=second, characteristic=density, value="1.5")
    for product in (first, second):
        client.post(reverse("compare_toggle", args=[product.id]), **AJAX)

    text = client.get(reverse("compare")).content.decode()
    assert "Alpha" in text and "Beta" in text
    assert "Плотность" in text and "1.2" in text and "1.5" in text
    assert "is-different" in text


@pytest.mark.django_db
def test_compare_page_empty(client):
    response = client.get(reverse("compare"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_remove_and_clear(client, make_product):
    first, second = make_product(name="Alpha"), make_product(name="Beta")
    for product in (first, second):
        client.post(reverse("compare_toggle", args=[product.id]), **AJAX)
    client.post(reverse("compare_remove", args=[first.id]))
    text = client.get(reverse("compare")).content.decode()
    assert "Beta" in text and "Alpha" not in text
    client.post(reverse("compare_clear"))
    assert "Beta" not in client.get(reverse("compare")).content.decode()


@pytest.mark.django_db
def test_product_page_has_active_compare_button(client, make_product):
    product = make_product()
    page = reverse("product", args=[product.id])
    assert 'compare-button' in client.get(page).content.decode()
    assert "compare-button is-active" not in client.get(page).content.decode()
    client.post(reverse("compare_toggle", args=[product.id]), **AJAX)
    assert "compare-button is-active" in client.get(page).content.decode()


@pytest.mark.django_db
def test_compare_page_is_translated_to_ukrainian(client):
    client.post("/i18n/setlang/", {"language": "uk", "next": "/"})
    text = client.get(reverse("compare")).content.decode()
    assert "Порівняння товарів" in text
    assert "Список порівняння порожній" in text
