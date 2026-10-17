import re

import pytest
from django.contrib.auth.models import User

USERNAME = "auth_test_user"
EMAIL = "auth_test_user@example.com"
PASSWORD = "S0meStrongPass!"


@pytest.mark.django_db
def test_home_page_offers_login_and_register(client):
    response = client.get("/")
    assert response.status_code == 200
    text = response.content.decode()
    assert 'id="registration-modal"' in text
    assert 'id="login-form"' in text
    assert 'id="registration-form"' in text


@pytest.mark.django_db
def test_anonymous_catalogue_and_search_dont_crash(client, make_product):
    """Регрессия: is_favorite=Exists(...user=request.user...) падал на
    AnonymousUser, потому что у неё нет pk, ORM-фильтру нужен user_id."""
    make_product()
    assert client.get("/catalogue/").status_code == 200
    assert client.get("/search/").status_code == 200


@pytest.mark.django_db
def test_register_creates_inactive_user_and_sends_activation_email(client, mailoutbox):
    response = client.post(
        "/register/",
        data={
            "username": USERNAME,
            "email": EMAIL,
            "password1": PASSWORD,
            "password2": PASSWORD,
            "city": "Odesa",
        },
        follow=True,
    )
    assert response.status_code == 200

    user = User.objects.get(username=USERNAME)
    assert user.is_active is False
    assert len(mailoutbox) == 1

    # регистрация больше не логинит мгновенно — требуется подтверждение
    assert client.get("/cabinet/").status_code == 302


@pytest.mark.django_db
def test_activation_link_activates_and_logs_in(client, mailoutbox):
    client.post(
        "/register/",
        data={
            "username": USERNAME, "email": EMAIL,
            "password1": PASSWORD, "password2": PASSWORD, "city": "Odesa",
        },
    )
    match = re.search(r"/activate/([^/]+)/([^/\s\"]+)/", mailoutbox[0].body)
    assert match is not None

    response = client.get(f"/activate/{match.group(1)}/{match.group(2)}/")
    assert response.status_code == 200
    assert "подтверждён" in response.content.decode()

    user = User.objects.get(username=USERNAME)
    assert user.is_active is True

    # activate() логинит пользователя сразу
    assert client.get("/cabinet/").status_code == 200


@pytest.mark.django_db
def test_invalid_activation_token_shows_error_without_crashing(client):
    user = User.objects.create_user(username=USERNAME, password=PASSWORD, is_active=False)
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    response = client.get(f"/activate/{uid}/not-a-real-token/")
    assert response.status_code == 200
    assert "недействительна" in response.content.decode()

    user.refresh_from_db()
    assert user.is_active is False


@pytest.mark.django_db
def test_login_and_logout(client):
    User.objects.create_user(username=USERNAME, password=PASSWORD, is_active=True)

    response = client.post("/login/", data={"username": USERNAME, "password": PASSWORD}, follow=True)
    assert response.status_code == 200
    assert client.get("/cabinet/").status_code == 200

    client.get("/logout/", follow=True)
    assert client.get("/cabinet/").status_code == 302
