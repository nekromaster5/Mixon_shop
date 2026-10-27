from django.conf import settings
from django.utils.functional import SimpleLazyObject

from .models import Brand


def google_maps(request):
    """Делает GOOGLE_MAPS_API_KEY доступным во всех шаблонах, чтобы ключ не
    был захардкожен в разметке."""
    return {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}


def brands(request):
    """Бренды для блока логотипов (главная, каталог, /brands/). Ленивый
    queryset: запрос в базу только на страницах, где блок выводится."""
    return {"brands": SimpleLazyObject(lambda: list(Brand.objects.all()))}
