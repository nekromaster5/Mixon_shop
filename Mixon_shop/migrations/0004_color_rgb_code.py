# Generated by Django 5.0.1 on 2024-07-22 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mixon_shop', '0003_color_volume_productstock_product_stocks'),
    ]

    operations = [
        migrations.AddField(
            model_name='color',
            name='rgb_code',
            field=models.CharField(default=6, max_length=50),
            preserve_default=False,
        ),
    ]
