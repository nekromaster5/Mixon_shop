# Mixon-shop

## Tests

Tests use SQLite in memory, so no MySQL is needed:

```bash
DJANGO_SETTINGS_MODULE=settings.test python manage.py test
```

They run on every push and pull request through GitHub Actions.
