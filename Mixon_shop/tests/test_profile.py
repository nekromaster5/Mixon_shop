import pytest


@pytest.mark.django_db
def test_profile_update_saves_fields(client, django_user_model, region):
    user1 = django_user_model.objects.create_user(username="user1", password="OldPass123!", email="user1@example.com")
    client.force_login(user1)

    response = client.post(
        "/cabinet/profile/",
        data={
            "first_name": "Иван", "last_name": "Петров", "email": "user1_new@example.com",
            "phone": "+380501234567", "company": "ТОВ Ромашка", "registration_number": "12345",
            "city": "Одесса", "postal_code": "65000", "region": region.id,
        },
        follow=True,
    )
    assert response.status_code == 200
    assert "tab=contact_information" in response.redirect_chain[-1][0]

    user1.refresh_from_db()
    assert user1.first_name == "Иван"
    assert user1.email == "user1_new@example.com"
    assert user1.userprofile.city == "Одесса"
    assert user1.userprofile.region_id == region.id


@pytest.mark.django_db
def test_profile_update_rejects_email_taken_by_another_user(client, django_user_model):
    user1 = django_user_model.objects.create_user(username="user1", password="pass12345", email="user1@example.com")
    django_user_model.objects.create_user(username="user2", password="pass12345", email="user2@example.com")
    client.force_login(user1)

    response = client.post(
        "/cabinet/profile/",
        data={"first_name": "", "last_name": "", "email": "user2@example.com", "city": "X"},
        follow=True,
    )
    user1.refresh_from_db()
    assert user1.email == "user1@example.com"
    assert "уже используется" in response.content.decode()


@pytest.mark.django_db
def test_password_change_requires_correct_old_password(client, django_user_model):
    user = django_user_model.objects.create_user(username="user1", password="OldPass123!")
    client.force_login(user)

    client.post(
        "/cabinet/password/",
        data={"old_password": "WRONG", "new_password1": "NewStrongPass456!", "new_password2": "NewStrongPass456!"},
    )
    user.refresh_from_db()
    assert user.check_password("OldPass123!")


@pytest.mark.django_db
def test_password_change_keeps_user_logged_in(client, django_user_model):
    """Регрессия: без update_session_auth_hash смена пароля разлогинила бы
    пользователя прямо в его кабинете."""
    user = django_user_model.objects.create_user(username="user1", password="OldPass123!")
    client.force_login(user)

    client.post(
        "/cabinet/password/",
        data={"old_password": "OldPass123!", "new_password1": "NewStrongPass456!", "new_password2": "NewStrongPass456!"},
    )
    user.refresh_from_db()
    assert user.check_password("NewStrongPass456!")
    assert client.get("/cabinet/").status_code == 200
