import pytest

from Mixon_shop.models import MENU_SECTIONS, Category, ProductType


@pytest.mark.django_db
def test_menu_sections_and_icons_are_fixed(client):
    text = client.get("/catalogue/").content.decode()
    for key, _label in MENU_SECTIONS:
        assert f'data-section="{key}"' in text
    assert "lkm-stroitelstvo" in text and "instrument" in text


@pytest.mark.django_db
def test_menu_shows_categories_and_types_of_their_section(client):
    wall = Category.objects.create(name="Краски для стен", menu_section="building")
    spray = Category.objects.create(name="Аэрозоли", menu_section="auto")
    facade = ProductType.objects.create(name="Фасадные краски")
    facade.categories.add(wall)
    enamel = ProductType.objects.create(name="Аэрозольные эмали")
    enamel.categories.add(spray)

    text = client.get("/catalogue/").content.decode()
    building = text.split('class="catalog-menu__types" data-section="building"')[1].split("catalog-menu__types")[0]
    assert "Краски для стен" in building
    assert f"?product_category_id={wall.id}&amp;type={facade.id}" in building
    assert "Аэрозоли" not in building
    assert f"?product_category_id={spray.id}&amp;type={enamel.id}" in text


@pytest.mark.django_db
def test_category_without_section_is_not_in_menu(client):
    Category.objects.create(name="Без раздела")
    assert "Без раздела" not in client.get("/catalogue/").content.decode()
