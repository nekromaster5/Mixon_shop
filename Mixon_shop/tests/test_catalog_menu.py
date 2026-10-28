import pytest

from Mixon_shop.models import Category, ProductType


@pytest.mark.django_db
def test_catalog_menu_shows_categories_and_their_types(client):
    building = Category.objects.create(name="ЛКМ для Строительства")
    auto = Category.objects.create(name="ЛКМ для Авторемонта")
    facade = ProductType.objects.create(name="Фасадные краски и грунты")
    facade.categories.add(building)
    enamel = ProductType.objects.create(name="Аэрозольные эмали")
    enamel.categories.add(building, auto)

    response = client.get("/catalogue/")
    assert response.status_code == 200
    text = response.content.decode()

    assert f'data-category-id="{building.id}"' in text
    assert f"?product_category_id={building.id}&amp;type={facade.id}" in text
    assert f"?product_category_id={auto.id}&amp;type={enamel.id}" in text
    # Тип показан только в своей категории.
    assert f"?product_category_id={auto.id}&amp;type={facade.id}" not in text
    # Для категории без логотипа берётся иконка из static по названию.
    assert "lkm-stroitelstvo%201.svg" in text or "lkm-stroitelstvo 1.svg" in text
