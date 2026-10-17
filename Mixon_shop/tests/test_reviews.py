import pytest
from django.contrib.auth.models import User

from Mixon_shop.models import Review


@pytest.mark.django_db
def test_average_rating_starts_at_zero(product):
    assert float(product.average_rating) == 0.0


@pytest.mark.django_db
def test_anonymous_review_requires_name(client, product):
    client.post(f"/product/{product.id}/submit_review/", data={"rating": "4", "review_text": "no name"})
    assert Review.objects.filter(product=product).count() == 0


@pytest.mark.django_db
def test_anonymous_review_with_name_is_accepted_and_updates_rating(client, product):
    client.post(
        f"/product/{product.id}/submit_review/",
        data={"rating": "4", "reviewer_name": "Гость", "phone": "+380000000000", "review_text": "anon review"},
    )
    review = Review.objects.get(product=product, user__isnull=True)
    assert review.reviewer_name == "Гость"
    assert review.display_name == "Гость"

    product.refresh_from_db()
    assert float(product.average_rating) == 4.0


@pytest.mark.django_db
@pytest.mark.parametrize("rating", ["0", "6", "not-a-number"])
def test_invalid_rating_rejected(client, product, rating):
    client.post(f"/product/{product.id}/submit_review/", data={"rating": rating, "reviewer_name": "X"})
    assert Review.objects.filter(product=product).count() == 0


@pytest.mark.django_db
def test_second_review_by_same_user_updates_instead_of_crashing(client, product, django_user_model):
    """Регрессия: unique_together('product', 'user') раньше давало IntegrityError
    на второй отзыв того же пользователя."""
    user = django_user_model.objects.create_user(username="reviewer", password="pass12345")
    client.force_login(user)

    client.post(f"/product/{product.id}/submit_review/", data={"rating": "2", "review_text": "first"})
    client.post(f"/product/{product.id}/submit_review/", data={"rating": "5", "review_text": "second"})

    assert Review.objects.filter(product=product, user=user).count() == 1
    review = Review.objects.get(product=product, user=user)
    assert review.rating == 5
    assert review.display_name == user.username


@pytest.mark.django_db
def test_deleting_review_recalculates_average(client, product):
    r1 = Review.objects.create(product=product, rating=4, reviewer_name="A")
    Review.objects.create(product=product, rating=2, reviewer_name="B")
    product.refresh_from_db()
    assert float(product.average_rating) == 3.0

    r1.delete()
    product.refresh_from_db()
    assert float(product.average_rating) == 2.0


@pytest.mark.django_db
def test_product_page_renders_star_widget_without_crashing(client, product):
    """Регрессия: product_detail() (нерабочая, не подключённая в urls.py)
    считала звёзды, а реально работающая ProductPage — нет."""
    Review.objects.create(product=product, rating=5, reviewer_name="A")
    response = client.get(f"/product/{product.id}/")
    assert response.status_code == 200
