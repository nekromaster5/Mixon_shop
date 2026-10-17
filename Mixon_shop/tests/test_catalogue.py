import pytest


@pytest.mark.django_db
def test_catalogue_paginates_at_twelve_per_page(client, make_product):
    products = [make_product(name=f"Product {i}") for i in range(15)]

    response = client.get("/catalogue/")
    assert response.status_code == 200
    text = response.content.decode()
    shown = sum(1 for p in products if f"/product/{p.id}/" in text)
    assert shown == 12

    response = client.get("/catalogue/?page=2")
    text = response.content.decode()
    shown = sum(1 for p in products if f"/product/{p.id}/" in text)
    assert shown == 3


@pytest.mark.django_db
@pytest.mark.parametrize("category_id", ["not-a-number", "999999"])
def test_garbage_or_missing_category_id_does_not_crash(client, category_id):
    """Регрессия: голый except: вокруг Category.objects.get(id=...) —
    теперь ловит конкретно DoesNotExist/ValueError/TypeError."""
    response = client.get(f"/catalogue/?product_category_id={category_id}")
    assert response.status_code == 200


@pytest.mark.django_db
def test_search_finds_product_by_name(client, make_product):
    make_product(name="Шпатлевка Уникальная")
    make_product(name="Грунт Универсальный")

    response = client.get("/search/?query=Шпатлевка")
    assert response.status_code == 200
    text = response.content.decode()
    assert "Шпатлевка Уникальная" in text
    assert "Грунт Универсальный" not in text
