import pytest

from Mixon_shop.models import (
    Branch, Category, Characteristic, City, FavoriteProduct, ProductCharacteristic, ProductParameter,
    ProductParameterImage, ProductParameterValue, ProductRequest, ProductTableRow,
)


@pytest.mark.django_db
def test_parameter_and_table_are_configured_in_admin(client, product):
    weight = ProductParameter.objects.create(name="Вага", unit="кг")
    product.parameter = weight
    product.table_title = "Відтінок"
    product.save()
    ProductParameterValue.objects.create(product=product, value="1.500")
    ProductParameterValue.objects.create(product=product, value="5")
    ProductTableRow.objects.create(product=product, vendor_code="MA603BAL", name="Хаки603", rgb_code="#6b6b3a")
    ProductTableRow.objects.create(product=product, vendor_code="MA100", name="Белый", rgb_code="#ffffff")

    text = client.get(f"/product/{product.id}/").content.decode()

    assert "Вага:" in text and "Відтінок:" in text
    assert "1.5 кг" in text and "5 кг" in text
    assert text.count("MA603BAL") == 1 and text.count("MA100") == 1
    assert 'class="pc-qty__input"' in text


@pytest.mark.django_db
def test_parameter_value_images_are_passed_to_the_page(client, product):
    value = ProductParameterValue.objects.create(product=product, value="3")
    ProductParameterImage.objects.create(parameter_value=value, image="products/parameters/three.png")

    text = client.get(f"/product/{product.id}/").content.decode()

    assert "products/parameters/three.png" in text


@pytest.mark.django_db
def test_product_without_stock_hides_color_and_package_blocks(client, product):
    text = client.get(f"/product/{product.id}/").content.decode()

    assert 'class="pc-table"' not in text
    assert 'package_block' not in text
    assert "MA603BAL" not in text
    assert "Немає фото" in text


@pytest.mark.django_db
def test_delivery_rows_have_distinct_names(client, product):
    text = client.get(f"/product/{product.id}/").content.decode()

    assert "Самовивіз із відділення" in text
    assert "Доставка до квартири" in text
    assert "Доставят до 01.07" not in text


@pytest.mark.django_db
def test_characteristics_come_from_category_list(client, product):
    density = Characteristic.objects.create(name="Щільність", order=2)
    density.categories.add(product.category)
    gloss = Characteristic.objects.create(name="Блиск", order=1)
    gloss.categories.add(product.category)
    empty = Characteristic.objects.create(name="Невикористана", order=3)
    empty.categories.add(product.category)
    ProductCharacteristic.objects.create(product=product, characteristic=density, value="1,5 кг/л")
    ProductCharacteristic.objects.create(product=product, characteristic=gloss, value="Матова")
    ProductCharacteristic.objects.create(product=product, characteristic=empty, value="")

    text = client.get(f"/product/{product.id}/").content.decode()

    assert "1,5 кг/л" in text
    assert text.index("Блиск") < text.index("Щільність")
    assert "Невикористана" not in text


@pytest.mark.django_db
def test_admin_adds_empty_rows_for_category_characteristics(admin_client, product):
    characteristic = Characteristic.objects.create(name="Щільність")
    characteristic.categories.add(product.category)
    other = Characteristic.objects.create(name="Чужа")
    other.categories.add(Category.objects.create(name="Other"))

    response = admin_client.get(f"/admin/Mixon_shop/product/{product.id}/change/")
    assert response.status_code == 200

    from Mixon_shop.admin import ProductAdmin
    from django.contrib.admin.sites import site
    request = response.wsgi_request
    form = type("Form", (), {"instance": product, "save_m2m": lambda self: None})()
    ProductAdmin(product.__class__, site).save_related(request, form, [], True)

    assert list(product.characteristic_values.values_list("characteristic__name", flat=True)) == ["Щільність"]


@pytest.mark.django_db
def test_quick_order_request_is_saved(client, product, branch):
    value = ProductParameterValue.objects.create(product=product, value="3")
    row = ProductTableRow.objects.create(product=product, vendor_code="MA603BAL", name="Хаки603")

    response = client.post(
        f"/product/{product.id}/request/",
        {"kind": "quick_order", "name": "Іван", "phone": "+380 67 123 45 67",
         "parameter_value": value.id, "row": row.id, f"quantity_{row.id}": 4},
    )

    assert response.json() == {"success": True}
    saved = ProductRequest.objects.get()
    assert (saved.kind, saved.phone) == ("quick_order", "+380 67 123 45 67")
    assert "3" in saved.selection and "MA603BAL" in saved.selection and "× 4" in saved.selection


@pytest.mark.django_db
def test_request_without_phone_is_rejected(client, product):
    response = client.post(f"/product/{product.id}/request/", {"kind": "cheaper", "name": "Іван", "phone": "123"})

    assert response.status_code == 400
    assert "phone" in response.json()["errors"]
    assert not ProductRequest.objects.exists()


@pytest.mark.django_db
def test_favorites_ajax_for_guest_returns_403(client, product):
    response = client.get(f"/manage-favorites/{product.id}", HTTP_X_REQUESTED_WITH="XMLHttpRequest")

    assert response.status_code == 403
    assert not FavoriteProduct.objects.exists()


@pytest.mark.django_db
def test_action_buttons_are_bound_to_product(client, product):
    text = client.get(f"/product/{product.id}/").content.decode()

    assert "compare--button" not in text
    assert "Шпатлевка универсальная 2 кг" not in text
    assert text.count(f'data-product-id="{product.id}"') >= 4
    assert 'data-request-kind="quick_order"' in text
    assert 'data-request-kind="cheaper"' in text
    assert "manageFavorites.js" in text
