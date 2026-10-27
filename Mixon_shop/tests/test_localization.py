import json

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_default_language_is_ukrainian(client, product):
    product.name_uk = "Українська назва"
    product.name_ru = "Русское название"
    product.save()

    response = client.get(f"/product/{product.id}/")
    assert response.status_code == 200
    text = response.content.decode()
    assert "Українська назва" in text
    assert "Русское название" not in text


@pytest.mark.django_db
def test_switching_language_changes_rendered_text(client, product):
    product.name_uk = "Українська назва"
    product.name_ru = "Русское название"
    product.save()

    response = client.post(
        reverse("set_language"),
        data={"language": "ru", "next": f"/product/{product.id}/"},
        follow=True,
    )
    assert response.status_code == 200
    text = response.content.decode()
    assert "Русское название" in text
    assert "Українська назва" not in text

    # выбор языка должен сохраняться в куке для последующих запросов
    response = client.get(f"/product/{product.id}/")
    assert "Русское название" in response.content.decode()


@pytest.mark.django_db
def test_language_switcher_buttons_present_on_home_page(client):
    response = client.get("/")
    assert response.status_code == 200
    text = response.content.decode()
    assert 'name="language" value="uk"' in text
    assert 'name="language" value="ru"' in text


@pytest.mark.django_db
def test_interface_strings_follow_selected_language(client):
    """Регрессия: при переключении на ru менялись только поля товаров
    (modeltranslation), а фильтры, шапка и подвал оставались как были."""
    text = client.get("/catalogue/").content.decode()
    assert "Фільтри" in text
    assert "Каталог товарів" in text
    assert "Оплата і доставка" in text

    client.post(reverse("set_language"), data={"language": "ru", "next": "/"})
    text = client.get("/catalogue/").content.decode()
    assert "Фильтры" in text
    assert "Каталог товаров" in text
    assert "Фільтри" not in text


@pytest.mark.django_db
def test_javascript_catalog_has_ukrainian_strings(client):
    text = client.get(reverse("javascript-catalog")).content.decode()
    # каталог отдаётся как JSON с \uXXXX-экранированием
    assert json.dumps("Товар додано до кошика!") in text
