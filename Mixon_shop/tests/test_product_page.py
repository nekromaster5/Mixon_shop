import pytest

from Mixon_shop.models import City, Branch, Color, ProductStock, Volume


@pytest.mark.django_db
def test_colors_come_from_stock_without_duplicates(client, product, branch):
    other_branch = Branch.objects.create(
        city=City.objects.create(name="Other"), address_short="Other", map_info="{}"
    )
    khaki = Color.objects.create(vendor_code="MA603BAL", name="Хаки603", rgb_code="#6b6b3a")
    white = Color.objects.create(vendor_code="MA100", name="Белый", rgb_code="#ffffff")
    one_liter = Volume.objects.create(size="1.00")
    ProductStock.objects.create(product=product, branch=branch, color=khaki, volume=one_liter, quantity=3)
    ProductStock.objects.create(product=product, branch=other_branch, color=khaki, volume=one_liter, quantity=2)
    ProductStock.objects.create(product=product, branch=branch, color=white, volume=one_liter, quantity=1)

    text = client.get(f"/product/{product.id}/").content.decode()

    assert text.count("MA603BAL") == 1
    assert text.count("MA100") == 1
    assert '<p class="table_quantity">5</p>' in text
    assert "1л." in text
    assert "3л." not in text


@pytest.mark.django_db
def test_product_without_stock_hides_color_and_package_blocks(client, product):
    text = client.get(f"/product/{product.id}/").content.decode()

    assert "Цвет:" not in text
    assert "Упаковка:" not in text
    assert "MA603BAL" not in text
    assert "Нет фото" in text


@pytest.mark.django_db
def test_delivery_rows_have_distinct_names(client, product):
    text = client.get(f"/product/{product.id}/").content.decode()

    assert "Курьерская доставка" in text
    assert "Доставка Новой почтой" in text
    assert "Доставят до 01.07" not in text
