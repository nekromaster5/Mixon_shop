# Generated by Django 5.0.1 on 2024-08-05 09:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mixon_shop', '0008_bindingsubstance_producttype'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Mixon_shop.producttype'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='product',
            name='binding_substance',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Mixon_shop.bindingsubstance'),
        ),
    ]