import pytest

from Mixon_shop.models import Brand


@pytest.fixture
def admin_client_(client, django_user_model):
    admin = django_user_model.objects.create_superuser(username="admin", email="admin@example.com", password="pass12345")
    client.force_login(admin)
    return client


@pytest.mark.django_db
def test_no_brands_by_default():
    # бренды заводит владелец магазина в админке, миграция ничего не создаёт
    assert not Brand.objects.exists()


@pytest.mark.django_db
def test_catalogue_filters_by_brand(client, make_product):
    mixon = Brand.objects.create(name="MIXON", slug="mixon")
    own = make_product(name="Краска A", brand=mixon)
    other = make_product(name="Краска B")

    text = client.get("/catalogue/?brand=mixon").content.decode()
    assert f"/product/{own.id}/" in text
    assert f"/product/{other.id}/" not in text


@pytest.mark.django_db
def test_unknown_brand_shows_all_products(client, make_product):
    product = make_product(name="Краска A")
    response = client.get("/catalogue/?brand=no-such-brand")
    assert response.status_code == 200
    assert f"/product/{product.id}/" in response.content.decode()


@pytest.mark.django_db
def test_brand_buttons_come_from_database(client):
    Brand.objects.create(name="Первый бренд", slug="first", order=1)
    Brand.objects.create(name="Второй бренд", slug="second", order=2)
    for path in ("/", "/catalogue/", "/brands/"):
        text = client.get(path).content.decode()
        assert "?brand=first" in text and "?brand=second" in text, path
        # без логотипа на кнопке выводится название
        assert "Первый бренд" in text, path
        assert text.index("?brand=first") < text.index("?brand=second"), path


@pytest.mark.django_db
def test_product_admin_has_brand_field(admin_client_):
    assert 'name="brand"' in admin_client_.get("/admin/Mixon_shop/product/add/").content.decode()
    assert admin_client_.get("/admin/Mixon_shop/product/").status_code == 200
    assert admin_client_.get("/admin/Mixon_shop/brand/").status_code == 200
