import pytest


@pytest.fixture
def admin_client_(client, django_user_model):
    admin = django_user_model.objects.create_superuser(username="admin", email="admin@example.com", password="pass12345")
    client.force_login(admin)
    return client


@pytest.mark.django_db
@pytest.mark.parametrize("path", [
    "/admin/Mixon_shop/product/add/",
    "/admin/Mixon_shop/category/add/",
    "/admin/Mixon_shop/producttype/add/",
    "/admin/Mixon_shop/bindingsubstance/add/",
    "/admin/Mixon_shop/news/add/",
    "/admin/Mixon_shop/newscategory/add/",
])
def test_translated_admin_add_pages_render(admin_client_, path):
    response = admin_client_.get(path)
    assert response.status_code == 200
    text = response.content.decode()
    # проверяем, что реально появились поля под оба языка, а не только базовое имя
    assert "_uk" in text
    assert "_ru" in text


@pytest.mark.django_db
def test_product_translated_fields_roundtrip(product):
    """name_uk/name_ru — настоящие поля модели, а не то же самое значение."""
    product.name_uk = "Українська назва"
    product.name_ru = "Русское название"
    product.save()
    product.refresh_from_db()
    assert product.name_uk == "Українська назва"
    assert product.name_ru == "Русское название"
