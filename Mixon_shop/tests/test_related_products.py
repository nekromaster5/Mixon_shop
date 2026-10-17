import pytest


@pytest.mark.django_db
def test_no_related_or_similar_products_shows_empty_state(client, product):
    response = client.get(f"/product/{product.id}/")
    assert response.status_code == 200
    text = response.content.decode()
    assert "не указаны сопутствующие товары" in text
    assert "не указаны похожие товары" in text


@pytest.mark.django_db
def test_related_and_similar_products_render_with_working_buy_buttons(client, make_product):
    main = make_product(name="Main")
    together = make_product(name="Together")
    similar = make_product(name="Similar")
    main.related_products.add(together)
    main.similar_products.add(similar)

    response = client.get(f"/product/{main.id}/")
    text = response.content.decode()
    assert together.name in text
    assert similar.name in text
    assert f'data-product-id="{together.id}"' in text
    assert f'data-product-id="{similar.id}"' in text
