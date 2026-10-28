# Mixon Shop

An online store built on Django 5: product catalogue with filters, cart, checkout with
delivery and payment options, promo codes, user accounts and a custom admin dashboard
for managing products, orders and content.

## Features

- **Catalogue**: categories, product types, filters (volume, binding substance and more),
  pagination and search by product name.
- **Product pages**: image gallery, characteristics, stock per branch, reviews,
  recommended products and sales leaders.
- **Cart**: session cart for guests and a database cart for signed-in users.
- **Checkout**: delivery and payment methods, promo codes with expiry dates,
  order creation through AJAX endpoints with server-side validation.
- **Users**: registration with email activation, login, password reset,
  personal cabinet and favourites.
- **Branches**: list of shops by region and city with weekly schedules and exceptions.
- **Content**: news with categories, main page banners and editable content blocks.
- **Admin**: customised dashboard and menu (django-admin-tools), drag-and-drop ordering
  (django-admin-sortable2).
- **Localisation**: Ukrainian and Russian.

## Tech stack

| Area      | Tools                                             |
|-----------|---------------------------------------------------|
| Backend   | Python 3, Django 5.0                              |
| Database  | MySQL (mysqlclient)                               |
| Frontend  | Django templates, JavaScript (AJAX)               |
| Static    | WhiteNoise                                        |
| Admin     | django-admin-tools, django-admin-sortable2        |
| Config    | python-dotenv, split settings (`base` / `dev` / `prod`) |

## Project structure

```
Mixon_shop/   Django app: models, views, forms, admin, cart logic, static files
settings/     base.py, dev.py, prod.py
server/       WSGI / ASGI entry points
templates/    HTML templates
media/        uploaded images
```

## Run locally

```bash
git clone https://github.com/nekromaster5/Mixon_shop.git
cd Mixon_shop
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.dist .env                   # then fill in SECRET_KEY and MySQL credentials
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000, and the admin panel at http://127.0.0.1:8000/admin.

`manage.py` uses development settings (`DEBUG = True`). The WSGI/ASGI entry points use
`settings.prod`.
