from django.contrib.auth.models import User
from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Product, ProductStock, Review, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


@receiver(post_save, sender=ProductStock)
@receiver(post_delete, sender=ProductStock)
def update_product_stock_status(sender, instance, **kwargs):
    product = instance.product
    # Проверка наличия товаров на складе
    if ProductStock.objects.filter(product=product).exists():
        product.is_in_stock = True
    else:
        product.is_in_stock = False
    product.save()


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_product_average_rating(sender, instance, **kwargs):
    """Пересчитывает средний рейтинг товара после сохранения/удаления отзыва —
    без этого product.average_rating так и остаётся 0.00 навсегда."""
    product = instance.product
    average = product.reviews.aggregate(average=Avg('rating'))['average']
    product.average_rating = round(average, 2) if average is not None else 0
    product.save(update_fields=['average_rating'])
