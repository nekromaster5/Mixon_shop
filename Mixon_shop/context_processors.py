from django.conf import settings


def google_maps(request):
    """Делает GOOGLE_MAPS_API_KEY доступным во всех шаблонах, чтобы ключ не
    был захардкожен в разметке."""
    return {"GOOGLE_MAPS_API_KEY": settings.GOOGLE_MAPS_API_KEY}
