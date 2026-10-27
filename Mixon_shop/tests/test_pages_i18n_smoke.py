import pytest
from django.contrib.auth.models import User
from django.urls import reverse

PAGES = ["home", "catalogue", "search", "brands", "news_list", "about_company", "checkout",
         "error", "shipment_and_payment", "contacts", "cart_detail", "cabinet"]


@pytest.mark.django_db
@pytest.mark.parametrize("language", ["uk", "ru"])
@pytest.mark.parametrize("page", PAGES)
def test_pages_render_in_both_languages(client, product, page, language):
    user = User.objects.create_user("i18n", "i18n@example.com", "pass12345")
    client.force_login(user)
    client.post(reverse("set_language"), data={"language": language, "next": "/"})
    response = client.get(reverse(page))
    # страница ошибки намеренно отдаёт 404
    assert response.status_code == (404 if page == "error" else 200)
