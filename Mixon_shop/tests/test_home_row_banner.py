import pytest

from Mixon_shop.models import HomeRowBanner, ProductImage, SalesLeaders


@pytest.fixture
def leaders(make_product):
    products = [make_product(name=f"Товар {i}", is_new=False) for i in range(4)]
    for product in products:
        ProductImage.objects.create(product=product, image="products/x.png")
        SalesLeaders.objects.create(product=product)
    return products


@pytest.mark.django_db
def test_banner_takes_fourth_place_in_row(client, leaders):
    HomeRowBanner.objects.create(section="sales_leaders", image="main_page/row_banners/b.png", link="/catalogue/")
    text = client.get("/").content.decode()
    assert text.count("home_row_banner__img") == 1
    assert f"/product/{leaders[2].id}/" in text
    assert f"/product/{leaders[3].id}/" not in text


@pytest.mark.django_db
def test_without_banner_row_keeps_all_products(client, leaders):
    text = client.get("/").content.decode()
    assert "home_row_banner__img" not in text
    assert f"/product/{leaders[3].id}/" in text


@pytest.mark.django_db
def test_unused_banner_is_hidden(client, leaders):
    HomeRowBanner.objects.create(section="sales_leaders", image="main_page/row_banners/b.png", is_used=False)
    assert "home_row_banner__img" not in client.get("/").content.decode()
