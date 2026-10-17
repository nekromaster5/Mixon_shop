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
