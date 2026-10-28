"""Проверка админки: каждая страница открывается, поиск и фильтры не падают,
товар сохраняется вместе с упаковками, цветами, брендом и характеристиками."""
from datetime import date, time

import pytest
from django.contrib import admin
from django.contrib.auth.models import Group
from django.urls import reverse

from Mixon_shop.models import (
    Brand, BranchSchedule, BranchScheduleException, Characteristic, Color, ContentBlock, EmailAddress,
    ErrorMessages, FavoriteProduct, InfoMessages, MainPageBanner, MainPageSections, News, NewsCategory, Order,
    OrderProduct, PhoneNumber, PromoCode, ProductCharacteristic, ProductImage, ProductParameter, ProductParameterImage,
    ProductParameterValue, ProductRequest, ProductTableRow, ProductStock,
    RecommendedProducts, Review, SalesLeaders, ScheduleTemplate, ScheduleTemplateItem, Volume, BindingSubstance,
)


@pytest.fixture
def superuser_client(client, django_user_model):
    user = django_user_model.objects.create_superuser(username="boss", email="boss@example.com", password="pass12345")
    client.force_login(user)
    return client


@pytest.fixture
def filled_db(product, branch, region, shipment_method, payment_method, order_status, django_user_model):
    """По одной записи каждой модели, чтобы открыть и список, и форму изменения."""
    brand = Brand.objects.create(name="Mixon", slug="mixon")
    product.brand = brand
    product.article = "MX-1"
    product.save()
    volume = Volume.objects.create(size="0.75")
    color = Color.objects.create(vendor_code="RAL 9003", name="Белый", rgb_code="#ffffff")
    ProductStock.objects.create(product=product, branch=branch, volume=volume, color=color, quantity=3)
    ProductImage.objects.create(product=product, image="products/images/test.png")
    product.parameter = ProductParameter.objects.create(name="Упаковка", unit="л")
    product.save()
    parameter_value = ProductParameterValue.objects.create(product=product, value="2.5")
    ProductParameterImage.objects.create(parameter_value=parameter_value, image="products/parameters/p.png")
    ProductTableRow.objects.create(product=product, vendor_code="RAL 9003", name="Белый", rgb_code="#ffffff")
    characteristic = Characteristic.objects.create(name="Сухой остаток")
    characteristic.categories.add(product.category)
    ProductCharacteristic.objects.create(product=product, characteristic=characteristic, value="50%")
    BindingSubstance.objects.create(name="Акрил")
    customer = django_user_model.objects.create_user(username="client", password="pass12345")
    Review.objects.create(product=product, user=customer, rating=5, review_text="Хорошая краска")
    FavoriteProduct.objects.create(user=customer, product=product)
    promo = PromoCode.objects.create(code="SALE10", discount_type="percentage", discount_value=10)
    order = Order.objects.create(
        name="Иван", phone="+380000000000", shipment_method=shipment_method, order_place=branch,
        payment_method=payment_method, goods_cost=100, shipment_cost=50, status=order_status, promo=promo,
    )
    OrderProduct.objects.create(order=order, product=product, quantity=2)
    ProductRequest.objects.create(kind="quick_order", product=product, volume=volume, color=color,
                                  name="Пётр", phone="+380111111111")
    SalesLeaders.objects.create(product=product)
    RecommendedProducts.objects.create(product=product)
    MainPageSections.objects.create(name=product.category)
    MainPageBanner.objects.create(image="main_page/images/banner.png", description="Баннер", is_used=True)
    news_category = NewsCategory.objects.create(name="Акции")
    news = News.objects.create(title="Новость", main_image="news/main_images/n.png", category=news_category)
    ContentBlock.objects.create(news=news, content_type="paragraph", text="Текст")
    template = ScheduleTemplate.objects.create(name="Будни")
    ScheduleTemplateItem.objects.create(template=template, day_of_week="MON", open_time=time(9), close_time=time(18))
    branch.schedule_template = template
    branch.save()
    BranchSchedule.objects.create(branch=branch, day_of_week="MON", open_time=time(9), close_time=time(18))
    BranchScheduleException.objects.create(branch=branch, date=date(2026, 12, 31), is_closed=True)
    branch.phone_numbers.add(PhoneNumber.objects.create(number="+380222222222"))
    branch.email.add(EmailAddress.objects.create(address="shop@example.com"))
    ErrorMessages.objects.create(name="err", message="Ошибка")
    InfoMessages.objects.create(name="info", message="Инфо")
    Group.objects.create(name="Менеджеры")
    return product


def registered_models():
    return sorted(admin.site._registry, key=lambda model: model._meta.label)


@pytest.mark.django_db
def test_admin_index_dashboard(superuser_client, filled_db):
    response = superuser_client.get(reverse("admin:index"))
    assert response.status_code == 200
    text = response.content.decode()
    for group in ("Заказы и заявки", "Товары", "Главная страница", "Магазины и контакты", "Быстрые действия"):
        assert group in text


@pytest.mark.django_db
def test_every_registered_model_is_on_dashboard():
    """Модель, которую забыли добавить в groups.py, на главной админки не видна."""
    from Mixon_shop.admin_tools.groups import GROUPS
    listed = {path for _, models in GROUPS for path in models}
    missing = [model._meta.label for model in registered_models()
               if f"{model.__module__}.{model.__name__}" not in listed]
    assert missing == []


@pytest.mark.django_db
@pytest.mark.parametrize("model", registered_models(), ids=lambda model: model._meta.label)
def test_admin_pages_open(superuser_client, filled_db, model):
    opts = model._meta
    changelist = reverse(f"admin:{opts.app_label}_{opts.model_name}_changelist")

    assert superuser_client.get(changelist).status_code == 200
    # поиск проверяет, что search_fields указывают на настоящие поля
    assert superuser_client.get(changelist, {"q": "a"}).status_code == 200
    assert superuser_client.get(reverse(f"admin:{opts.app_label}_{opts.model_name}_add")).status_code == 200

    obj = model.objects.first()
    assert obj is not None, f"нет тестовой записи для {opts.label}"
    change = reverse(f"admin:{opts.app_label}_{opts.model_name}_change", args=[obj.pk])
    assert superuser_client.get(change).status_code == 200


def management_form(prefix, total, initial=0):
    return {
        f"{prefix}-TOTAL_FORMS": str(total), f"{prefix}-INITIAL_FORMS": str(initial),
        f"{prefix}-MIN_NUM_FORMS": "0", f"{prefix}-MAX_NUM_FORMS": "1000",
    }


@pytest.mark.django_db
def test_product_saved_with_packages_colors_brand_and_characteristics(superuser_client, category, product_type,
                                                                        branch):
    brand = Brand.objects.create(name="Mixon", slug="mixon")
    small, big = Volume.objects.create(size="0.75"), Volume.objects.create(size="2.5")
    white = Color.objects.create(vendor_code="RAL 9003", name="Белый", rgb_code="#ffffff")
    dry = Characteristic.objects.create(name="Сухой остаток", order=1)
    dry.categories.add(category)
    drying = Characteristic.objects.create(name="Время высыхания", order=2)
    drying.categories.add(category)

    data = {
        "name_uk": "Фарба біла", "name_ru": "Краска белая", "article": "MX-100",
        "category": category.pk, "type": product_type.pk, "brand": brand.pk,
        "price": "450.00", "discount_price": "399.00", "is_discounted": "on", "is_new": "on",
        "description_uk": "Опис", "description_ru": "Описание",
        **management_form("images", 0),
        "parameter": "", "table_title_uk": "Відтінок", "table_title_ru": "Оттенок",
        **management_form("parameter_values", 2),
        "parameter_values-0-value": "1", "parameter_values-0-order": "0",
        "parameter_values-1-value": "5", "parameter_values-1-order": "1",
        **management_form("table_rows", 1),
        "table_rows-0-vendor_code": "RAL 9003", "table_rows-0-name": "Белый", "table_rows-0-order": "0",
        **management_form("productstock_set", 2),
        "productstock_set-0-branch": branch.pk, "productstock_set-0-volume": small.pk,
        "productstock_set-0-color": white.pk, "productstock_set-0-quantity": "5",
        "productstock_set-1-branch": branch.pk, "productstock_set-1-volume": big.pk,
        "productstock_set-1-quantity": "2",
        **management_form("characteristic_values", 1),
        "characteristic_values-0-characteristic": dry.pk,
        "characteristic_values-0-value_uk": "55%", "characteristic_values-0-value_ru": "55%",
        "_save": "Сохранить",
    }
    response = superuser_client.post(reverse("admin:Mixon_shop_product_add"), data)
    assert response.status_code == 302, response.context["adminform"].form.errors if response.context else response

    from Mixon_shop.models import Product
    product = Product.objects.get(article="MX-100")
    assert product.brand == brand
    assert product.name_ru == "Краска белая"
    assert product.is_discounted and product.discount_price == 399
    assert product.is_in_stock  # проставляется по строкам наличия
    stocks = set(ProductStock.objects.filter(product=product).values_list("volume__size", "color__name", "quantity"))
    assert {(float(size), color, qty) for size, color, qty in stocks} == {(0.75, "Белый", 5), (2.5, None, 2)}
    values = {name: value or "" for name, value
              in product.characteristic_values.values_list("characteristic__name", "value_ru")}
    # заполненная характеристика сохранилась, а для второй из категории добавилась пустая строка
    assert values == {"Сухой остаток": "55%", "Время высыхания": ""}

    # форма изменения открывается и показывает сохранённые строки
    response = superuser_client.get(reverse("admin:Mixon_shop_product_change", args=[product.pk]))
    assert response.status_code == 200
    assert "RAL 9003" in response.content.decode()
    assert [str(v.value) for v in product.parameter_values.all()] == ["1.000", "5.000"]
    assert product.table_rows.get().vendor_code == "RAL 9003" and product.table_title_ru == "Оттенок"


@pytest.mark.django_db
def test_order_status_editable_from_list(superuser_client, filled_db, order_status):
    from Mixon_shop.models import OrderStatus
    done = OrderStatus.objects.create(name="Выполнен")
    order = Order.objects.get()
    data = {
        **management_form("form", 1, 1),
        "form-0-id": order.pk, "form-0-status": done.pk, "_save": "Сохранить",
    }
    response = superuser_client.post(reverse("admin:Mixon_shop_order_changelist"), data)
    assert response.status_code == 302
    order.refresh_from_db()
    assert order.status == done


@pytest.mark.django_db
def test_news_edit_keeps_working(superuser_client, filled_db):
    """Раньше News.save искал старую запись в NewsCategory и падал при изменении новости."""
    news = News.objects.get()
    news.title = "Новый заголовок"
    news.save()
    news.refresh_from_db()
    assert news.slug == "novyi-zagolovok"
