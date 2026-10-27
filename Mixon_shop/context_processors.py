from django.conf import settings
from django.utils.functional import SimpleLazyObject

from .models import Brand, Category


def google_maps(request):
    """Делает GOOGLE_MAPS_API_KEY доступным во всех шаблонах, чтобы ключ не
    был захардкожен в разметке."""
    return {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}


def brands(request):
    """Бренды для блока логотипов (главная, каталог, /brands/). Ленивый
    queryset: запрос в базу только на страницах, где блок выводится."""
    return {"brands": SimpleLazyObject(lambda: list(Brand.objects.all()))}


# Иконки по умолчанию для категорий без загруженного логотипа: ключ — часть
# названия категории (без учёта регистра), значение — файл в static.
CATEGORY_FALLBACK_ICONS = (
    ('строит', 'src/assets/img/icon/lkm-stroitelstvo 1.svg'),
    ('будів', 'src/assets/img/icon/lkm-stroitelstvo 1.svg'),
    ('авторем', 'src/assets/img/icon/lkm-autoremont 1.svg'),
    ('древо', 'src/assets/img/icon/lkm-derevo 1.svg'),
    ('дерев', 'src/assets/img/icon/lkm-derevo 1.svg'),
    ('промыш', 'src/assets/img/icon/lkm-industry 1.svg'),
    ('промисл', 'src/assets/img/icon/lkm-industry 1.svg'),
    ('химия', 'src/assets/img/icon/auto-chemikal 1.svg'),
    ('хімія', 'src/assets/img/icon/auto-chemikal 1.svg'),
    ('инструм', 'src/assets/img/icon/instrument 1.svg'),
    ('інструм', 'src/assets/img/icon/instrument 1.svg'),
)


def catalog_menu(request):
    """Категории с их типами товаров для выпадающего меню «Каталог товаров»."""
    categories = list(Category.objects.prefetch_related('product_types').order_by('id'))
    for category in categories:
        name = category.name.lower()
        category.fallback_icon = next(
            (icon for key, icon in CATEGORY_FALLBACK_ICONS if key in name), None
        )
    return {"catalog_menu_categories": categories}
