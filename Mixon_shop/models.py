import string
from random import choice

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


# Region model
class Region(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=18, null=True, blank=True)
    company = models.CharField(max_length=256, null=True, blank=True)
    registration_number = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()


# PhoneNumber model
class PhoneNumber(models.Model):
    number = models.CharField(max_length=18)

    def __str__(self):
        return self.number


# Branch model
class Branch(models.Model):
    city = models.CharField(max_length=256)
    address = models.CharField(max_length=512)
    working_hours = models.CharField(max_length=256)
    phone_numbers = models.ManyToManyField(PhoneNumber)
    map_info = models.TextField()


# Product model
class Product(models.Model):
    description = models.TextField()
    usage = models.CharField(max_length=256)
    binding_substance = models.CharField(max_length=256)
    dry_residue = models.CharField(max_length=256)
    density = models.CharField(max_length=256)
    drying_time = models.CharField(max_length=256)
    consumption = models.CharField(max_length=256)
    solvent = models.CharField(max_length=256)
    working_tools = models.CharField(max_length=256)
    tool_cleaning = models.CharField(max_length=256)
    storage = models.CharField(max_length=256)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_discounted = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    images = models.ImageField(upload_to='products/images/', blank=True, null=True)
    related_products = models.ManyToManyField('self', blank=True)
    similar_products = models.ManyToManyField('self', blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)


# Review model
class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review_text = models.TextField(blank=True, null=True)
    pros = models.TextField(blank=True, null=True)
    cons = models.TextField(blank=True, null=True)
    rating = models.IntegerField()

    class Meta:
        unique_together = ('product', 'user')


# Order status model
class OrderStatus(models.Model):
    name = models.CharField(max_length=256)


# Order model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


# Favorite products model
class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


# Product comparison model
class ProductComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)


# News category model
class NewsCategory(models.Model):
    name = models.CharField(max_length=256)


# News model
class News(models.Model):
    title = models.CharField(max_length=256)
    main_image = models.ImageField(upload_to='news/main_images/')
    images = models.ImageField(upload_to='news/images/', blank=True, null=True)
    text = models.TextField()
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE)
    date_published = models.DateTimeField(auto_now_add=True)


class ErrorMessages(models.Model):
    name = models.CharField(verbose_name=_('error`s short name'), max_length=100, unique=True)
    full_text = models.CharField(verbose_name=_('error`s full text'), max_length=255)


class InfoMessages(models.Model):
    name = models.CharField(verbose_name=_('message`s short name'), max_length=100, unique=True)
    full_text = models.CharField(verbose_name=_('message`s full text'), max_length=255)

# def rand_slug():
#     return ''.join(choice(string.ascii_letters + string.digits) for _ in range(12))
#
#
# def rand_title_chars(value):
#     return ''.join(choice(value) for _ in range(int(len(value)/2)))
