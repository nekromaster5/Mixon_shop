from django.db import migrations

# Старые фиксированные поля товара -> характеристики по категориям.
# (поле, порядок, название uk, название ru)
FIELDS = [
    ('usage', 10, 'Призначення', 'Использование'),
    ('binding_substance', 20, "Зв'язуюча речовина", 'Связующее вещество'),
    ('dry_residue', 30, 'Сухий залишок', 'Сухой остаток'),
    ('density', 40, 'Щільність', 'Плотность'),
    ('drying_time', 50, 'Час висихання', 'Время высыхания'),
    ('consumption', 60, 'Витрата', 'Расход'),
    ('solvent', 70, 'Розчинник', 'Разбавитель'),
    ('working_tools', 80, 'Робочі інструменти', 'Рабочие инструменты'),
    ('tool_cleaning', 90, 'Очищення інструментів', 'Очистка рабочих инструментов'),
    ('storage', 100, 'Зберігання', 'Хранение'),
]


def forwards(apps, schema_editor):
    Product = apps.get_model('Mixon_shop', 'Product')
    Characteristic = apps.get_model('Mixon_shop', 'Characteristic')
    ProductCharacteristic = apps.get_model('Mixon_shop', 'ProductCharacteristic')

    for product in Product.objects.select_related('binding_substance'):
        for field, order, name_uk, name_ru in FIELDS:
            if field == 'binding_substance':
                substance = product.binding_substance
                if substance is None:
                    continue
                value = substance.name_uk or substance.name_ru or substance.name
                value_uk = substance.name_uk or value
                value_ru = substance.name_ru or value
            elif field == 'usage':
                value = product.usage_uk or product.usage_ru or product.usage
                value_uk = product.usage_uk or value
                value_ru = product.usage_ru or value
            else:
                value = value_uk = value_ru = getattr(product, field)
            if not value:
                continue

            characteristic, _ = Characteristic.objects.get_or_create(
                name_uk=name_uk,
                defaults={'name': name_uk, 'name_ru': name_ru, 'order': order},
            )
            characteristic.categories.add(product.category_id)
            ProductCharacteristic.objects.get_or_create(
                product=product,
                characteristic=characteristic,
                defaults={'value': value_uk, 'value_uk': value_uk, 'value_ru': value_ru},
            )


class Migration(migrations.Migration):
    dependencies = [
        ('Mixon_shop', '0042_product_characteristics_and_requests'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
