# Mixon Shop

Интернет-магазин лакокрасочных материалов и автохимии на Django 5.

## Быстрый старт (разработка)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/macOS

pip install -r requirements-dev.txt   # requirements.txt + инструменты для тестов
copy .env.dist .env                    # Windows: copy, Linux/macOS: cp
```

Откройте `.env` и задайте хотя бы `SECRET_KEY` (любую случайную строку). Остальные переменные
необязательны для локальной разработки — без них письма печатаются в консоль, карта не
подгружается, а база — SQLite (`db.sqlite3`).

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

По умолчанию используются настройки `settings.dev` (`DEBUG=True`). Сайт — на `http://127.0.0.1:8000/`,
админка — на `/admin/`.

## Переменные окружения

Полный список — в [.env.dist](.env.dist) с комментариями. Кратко:

| Переменная | Обязательна | Назначение |
|---|---|---|
| `SECRET_KEY` | всегда | секретный ключ Django |
| `DB_ENGINE=mysql` + `DB_*` | только для `settings.prod` | переключает базу с SQLite на MySQL |
| `ALLOWED_HOSTS` | только для `settings.prod` | домены сайта через запятую |
| `EMAIL_*` | нет | без них письма только печатаются в консоль |
| `GOOGLE_MAPS_API_KEY` | нет | без ключа карта филиалов просто не подгружается |
| `LOG_TO_FILE=true` | нет | дополнительно пишет логи в `logs/app.log` |

`settings.prod` **откажется запускаться**, если не заданы `SECRET_KEY` и `ALLOWED_HOSTS` — это
осознанная защита от случайного запуска прод-сервера с настройками для разработки.

## Тесты

```bash
pytest -v
```

Тесты лежат в `Mixon_shop/tests/`, используют `pytest-django` и полностью изолированы от
`db.sqlite3` (своя тестовая БД в памяти на каждый запуск). Прогоняются автоматически в
GitHub Actions на каждый push/PR ([.github/workflows/tests.yml](.github/workflows/tests.yml)).

## Локализация (uk/ru)

Каталог, категории и новости — двуязычные (`django-modeltranslation`). Переключатель языка —
кнопки «Укр»/«Рус» в шапке, выбор сохраняется в куке на год.

- Какие поля переводятся — [Mixon_shop/translation.py](Mixon_shop/translation.py). Чтобы
  добавить ещё одно поле: впишите его в нужный `TranslationOptions.fields`, затем
  `python manage.py makemigrations && python manage.py migrate`.
- В админке переводимые поля появляются как `name_uk`/`name_ru` и т.п. — отдельное поле на
  каждый язык, без переключателя вкладок.
- При переносе существующих данных из старой (не двуязычной) базы — один раз выполните
  `python manage.py update_translation_fields`, это скопирует значение из исходного поля
  (`name`) в поле языка по умолчанию (`name_uk`).

## Структура проекта

- `Mixon_shop/` — единственное Django-приложение: модели, вьюхи, шаблонные теги, тесты.
- `settings/` — `base.py` (общее), `dev.py` (локальная разработка), `prod.py` (продакшен).
- `templates/` — HTML-шаблоны (Django Template Language).
- `Mixon_shop/static/src/` — статика: CSS (уже скомпилированный, `assets/scss` — источники,
  но сборочный пайплайн в репозиторий не входит), JS, изображения.
- `media/` — загружаемые пользователями/админкой файлы (изображения товаров, новостей и т.д.).

## Продакшен

Кратко (подробности — в `settings/prod.py` и `.env.dist`):

1. `DJANGO_SETTINGS_MODULE=settings.prod`.
2. Обязательно: `SECRET_KEY`, `ALLOWED_HOSTS` в `.env`.
3. `python manage.py collectstatic` — соберёт статику в `static/` (отдаётся через `whitenoise`).
4. Запуск через `gunicorn server.wsgi:application` за реверс-прокси (nginx и т.п.) с HTTPS.
5. Сайт стоит за HTTPS — иначе выключите `SECURE_SSL_REDIRECT=false` в `.env`, но это не
   рекомендуется.
