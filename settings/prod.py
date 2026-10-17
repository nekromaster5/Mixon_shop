from django.core.exceptions import ImproperlyConfigured

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

if SECRET_KEY == "empty_secret_key":
    raise ImproperlyConfigured(
        "SECRET_KEY не задан в .env — сгенерируйте свой ключ и добавьте его в "
        "переменные окружения перед запуском в проде (см. .env.dist)."
    )

_allowed_hosts = os.getenv("ALLOWED_HOSTS", "")
if not _allowed_hosts:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS не задан в .env — укажите домен(ы) сайта через запятую, "
        "например: ALLOWED_HOSTS=mixon-shop.com,www.mixon-shop.com"
    )
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts.split(",") if host.strip()]

_csrf_trusted = os.getenv("CSRF_TRUSTED_ORIGINS", "")
if _csrf_trusted:
    CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in _csrf_trusted.split(",") if origin.strip()]

STATIC_ROOT = BASE_DIR / 'static/'

# ---- HTTPS/безопасность -------------------------------------------------
# Включены по умолчанию: сайт на проде должен стоять за HTTPS (см. пункт
# про домен/сертификат в списке того, что требует внешнего хостинга).
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "true").lower() == "true"
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30  # 30 дней — можно наращивать постепенно
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Если сайт стоит за обратным прокси (nginx/балансировщик), который сам
# терминирует HTTPS и проксирует на gunicorn по HTTP — включите этот флаг,
# иначе Django будет считать все запросы нешифрованными и зациклит редирект.
if os.getenv("BEHIND_HTTPS_PROXY", "false").lower() == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
