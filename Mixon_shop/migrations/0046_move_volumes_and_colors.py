"""Перенос упаковок и цветов из строк наличия в новые параметры товара.

Раньше кнопки «Упаковка» и таблица «Цвет» на странице товара строились из ProductStock.
Теперь у товара свой параметр (по умолчанию «Упаковка», л) со значениями и своя таблица строк.
Строки наличия не трогаем: они по-прежнему нужны для остатков и фильтра каталога.
"""
from django.db import migrations


def forwards(apps, schema_editor):
    Product = apps.get_model('Mixon_shop', 'Product')
    ProductStock = apps.get_model('Mixon_shop', 'ProductStock')
    ProductParameter = apps.get_model('Mixon_shop', 'ProductParameter')
    ProductParameterValue = apps.get_model('Mixon_shop', 'ProductParameterValue')
    ProductTableRow = apps.get_model('Mixon_shop', 'ProductTableRow')
    ProductRequest = apps.get_model('Mixon_shop', 'ProductRequest')

    package = None
    for product in Product.objects.filter(productstock__isnull=False).distinct():
        stocks = ProductStock.objects.filter(product=product)

        sizes = sorted({s.volume.size for s in stocks.select_related('volume') if s.volume_id})
        if sizes:
            if package is None:
                package = ProductParameter.objects.filter(name_uk='Упаковка', unit_uk='л').first()
                if package is None:
                    package = ProductParameter.objects.create(
                        name='Упаковка', name_uk='Упаковка', name_ru='Упаковка',
                        unit='л', unit_uk='л', unit_ru='л',
                    )
            if product.parameter_id is None:
                product.parameter = package
                product.save(update_fields=['parameter'])
            for order, size in enumerate(sizes):
                ProductParameterValue.objects.get_or_create(product=product, value=size, defaults={'order': order})

        colors = {s.color_id: s.color for s in stocks.select_related('color') if s.color_id}
        ordered = sorted(colors.values(), key=lambda c: (c.vendor_code, c.name))
        for order, color in enumerate(ordered):
            ProductTableRow.objects.get_or_create(
                product=product, vendor_code=color.vendor_code, name=color.name,
                defaults={'rgb_code': color.rgb_code, 'order': order},
            )

    for request in ProductRequest.objects.filter(selection='').exclude(volume=None, color=None):
        parts = []
        if request.volume_id:
            parts.append(f'Упаковка: {request.volume.size.normalize():f} л')
        if request.color_id:
            parts.append(f'Цвет: {request.color.vendor_code} {request.color.name}')
        request.selection = '; '.join(parts)
        request.save(update_fields=['selection'])


class Migration(migrations.Migration):

    dependencies = [
        ('Mixon_shop', '0045_product_parameters_and_table'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
