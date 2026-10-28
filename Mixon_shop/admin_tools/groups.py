"""Разделы админки: одни и те же группы на главной странице админки и в верхнем меню.

Чтобы перенести модель в другой раздел, достаточно поправить этот список.
"""

GROUPS = (
    ('Заказы и заявки', (
        'Mixon_shop.models.Order',
        'Mixon_shop.models.ProductRequest',
        'Mixon_shop.models.Review',
    )),
    ('Товары', (
        'Mixon_shop.models.Product',
        'Mixon_shop.models.Category',
        'Mixon_shop.models.Brand',
        'Mixon_shop.models.Characteristic',
        'Mixon_shop.models.ProductParameter',
        'Mixon_shop.models.Color',
        'Mixon_shop.models.Volume',
        'Mixon_shop.models.ProductType',
        'Mixon_shop.models.BindingSubstance',
        'Mixon_shop.models.ProductStock',
    )),
    ('Главная страница', (
        'Mixon_shop.models.MainPageBanner',
        'Mixon_shop.models.MainPageSections',
        'Mixon_shop.models.SalesLeaders',
        'Mixon_shop.models.RecommendedProducts',
    )),
    ('Новости', (
        'Mixon_shop.models.News',
        'Mixon_shop.models.NewsCategory',
    )),
    ('Магазины и контакты', (
        'Mixon_shop.models.Branch',
        'Mixon_shop.models.ScheduleTemplate',
        'Mixon_shop.models.City',
        'Mixon_shop.models.PhoneNumber',
        'Mixon_shop.models.EmailAddress',
    )),
    ('Настройки заказа', (
        'Mixon_shop.models.OrderStatus',
        'Mixon_shop.models.ShipmentMethod',
        'Mixon_shop.models.PaymentMethod',
        'Mixon_shop.models.PromoCode',
    )),
    ('Покупатели', (
        'django.contrib.auth.models.User',
        'Mixon_shop.models.UserProfile',
        'Mixon_shop.models.Region',
        'Mixon_shop.models.FavoriteProduct',
    )),
    ('Служебное', (
        'Mixon_shop.models.ErrorMessages',
        'Mixon_shop.models.InfoMessages',
        'Mixon_shop.models.ProductImage',
        'Mixon_shop.models.ProductParameterValue',
        'django.contrib.auth.models.Group',
    )),
)

# Свёрнуты на главной странице админки, чтобы не отвлекать
COLLAPSED = {'Покупатели', 'Служебное'}
