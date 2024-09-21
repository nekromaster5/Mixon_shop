# Generated by Django 5.0.1 on 2024-08-05 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Mixon_shop', '0007_product_is_in_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='BindingSubstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='ProductType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
        ),
    ]