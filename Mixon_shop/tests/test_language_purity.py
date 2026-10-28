import re
from pathlib import Path

import polib
import pytest
from django.contrib.auth.models import User
from django.urls import reverse

LOCALE = Path(__file__).resolve().parents[2] / 'locale'
UK_LETTERS = re.compile(r'[іїєґІЇЄҐ]')
RU_LETTERS = re.compile(r'[ыэъёЫЭЪЁ]')
CATALOGS = ['django', 'djangojs']


def entries(lang, name):
    return {e.msgid: e for e in polib.pofile(str(LOCALE / lang / 'LC_MESSAGES' / f'{name}.po')) if not e.obsolete and e.msgid}


@pytest.mark.parametrize('name', CATALOGS)
def test_ru_catalog_has_every_string(name):
    """Если строки нет в ru-каталоге, Django берёт перевод из LANGUAGE_CODE='uk' и в русской версии
    появляются украинские слова."""
    missing = set(entries('uk', name)) - set(entries('ru', name))
    assert not missing, sorted(missing)[:10]


@pytest.mark.parametrize('name', CATALOGS)
def test_catalogs_are_complete_and_not_mixed(name):
    for lang, foreign in (('uk', RU_LETTERS), ('ru', UK_LETTERS)):
        for msgid, entry in entries(lang, name).items():
            assert entry.msgstr, f'{lang}: нет перевода «{msgid}»'
            assert 'fuzzy' not in entry.flags, f'{lang}: неточный перевод «{msgid}»'
            assert not foreign.search(entry.msgstr), f'{lang}: «{msgid}» → «{entry.msgstr}»'


@pytest.mark.django_db
@pytest.mark.parametrize('language, foreign', [('ru', UK_LETTERS), ('uk', RU_LETTERS)])
@pytest.mark.parametrize('page', ['home', 'catalogue', 'brands', 'news_list', 'about_company', 'checkout',
                                  'shipment_and_payment', 'contacts', 'cart_detail', 'compare', 'cabinet'])
def test_pages_have_no_foreign_letters(client, product, page, language, foreign):
    user = User.objects.create_user('purity', 'purity@example.com', 'pass12345')
    client.force_login(user)
    client.post(reverse('set_language'), data={'language': language, 'next': '/'})
    html = client.get(reverse(page)).content.decode()
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    html = re.sub(r'<(script|style)\b.*?</\1>', '', html, flags=re.S)
    text = re.sub(r'<[^>]+>', ' ', html)
    # имя тестового пользователя и данные — латиницей, поэтому чужие буквы могут быть только из интерфейса
    assert not foreign.findall(text), sorted(set(re.findall(r'\S*' + foreign.pattern + r'\S*', text)))[:10]
