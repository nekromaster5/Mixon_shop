from django.conf import settings
from django.utils.functional import SimpleLazyObject

from django.utils.translation import gettext_lazy as _

from .models import MENU_SECTIONS, Brand, Category
from .session_compare import SessionCompare


def google_maps(request):
    """Делает GOOGLE_MAPS_API_KEY доступным во всех шаблонах, чтобы ключ не
    был захардкожен в разметке."""
    return {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}


def brands(request):
    """Бренды для блока логотипов (главная, каталог, /brands/). Ленивый
    queryset: запрос в базу только на страницах, где блок выводится."""
    return {"brands": SimpleLazyObject(lambda: list(Brand.objects.all()))}


# Иконки фиксированных разделов меню «Каталог товаров» (файлы в static).
MENU_SECTION_ICONS = {
    'building': 'src/assets/img/icon/lkm-stroitelstvo 1.svg',
    'auto': 'src/assets/img/icon/lkm-autoremont 1.svg',
    'wood': 'src/assets/img/icon/lkm-derevo 1.svg',
    'industry': 'src/assets/img/icon/lkm-industry 1.svg',
    'autochem': 'src/assets/img/icon/auto-chemikal 1.svg',
    'tools': 'src/assets/img/icon/instrument 1.svg',
}


def catalog_menu(request):
    """Меню «Каталог товаров»: слева фиксированные разделы с иконками, справа при
    наведении категории раздела (из админки) и их типы товаров."""
    categories = Category.objects.exclude(menu_section='').prefetch_related('product_types').order_by('id')
    by_section = {}
    for category in categories:
        by_section.setdefault(category.menu_section, []).append(category)
    sections = [
        {
            'key': key,
            'label': _(label),
            'icon': MENU_SECTION_ICONS[key],
            'categories': by_section.get(key, []),
        }
        for key, label in MENU_SECTIONS
    ]
    return {"catalog_menu_sections": sections}


def compare(request):
    """id товаров в списке сравнения: для счётчика в шапке и подсветки кнопок."""
    ids = SessionCompare(request).ids
    return {"compare_ids": ids, "compare_count": len(ids)}
