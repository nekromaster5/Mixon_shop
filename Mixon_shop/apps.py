from django.apps import AppConfig


class MixonShopConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Mixon_shop'

    def ready(self):
        from . import signals  # noqa: F401 — регистрирует обработчики сигналов
