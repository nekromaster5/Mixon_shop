import string
import random
from random import choice

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from unidecode import unidecode
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Region model
class Region(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='')
    phone = models.CharField(max_length=18, null=True, blank=True)
    company = models.CharField(max_length=256, null=True, blank=True)
    registration_number = models.CharField(max_length=256, null=True, blank=True)
    city = models.CharField(max_length=256)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.user.first_name}, {self.user.last_name}'


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


# EmailAddress model
class EmailAddress(models.Model):
    address = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return self.address


class City(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


# # Branch model
# class Branch(models.Model):
#     city = models.ForeignKey(City, on_delete=models.CASCADE)
#     address = models.CharField(max_length=512)
#     working_hours = models.CharField(max_length=256)
#     phone_numbers = models.ManyToManyField(PhoneNumber)
#     map_info = models.TextField()
#
#     def __str__(self):
#         return f'{self.city.name}, {self.address}'

class Branch(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    address_base = models.CharField(max_length=512, verbose_name='Основной адрес', blank=True, null=True)
    address_detail = models.CharField(max_length=512, verbose_name='Уточняющий адрес', blank=True, null=True)
    address_short = models.CharField(max_length=512, verbose_name='Сокращенный адрес')
    phone_numbers = models.ManyToManyField(PhoneNumber, blank=True)
    email = models.ManyToManyField(EmailAddress, blank=True)
    map_info = models.TextField()
    schedule_template = models.ForeignKey(
        'ScheduleTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_('Optional template for standard schedule')
    )

    def __str__(self):
        return f'{self.address_short}, {self.city.name}'

    def get_schedule(self, specific_date=None, day_of_week=None):
        """
        Получить расписание:
        - для конкретной даты (с учетом исключений),
        - для дня недели,
        - или всё расписание филиала.
        """
        from datetime import datetime
        if specific_date:
            exception = self.schedule_exceptions.filter(date=specific_date).first()
            if exception:
                return exception
            # Если исключения нет, продолжаем с обычным расписанием для дня недели
            weekday = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'][specific_date.weekday()]
            day_of_week = weekday

        if day_of_week:
            # Сначала ищем индивидуальное расписание
            schedule = self.schedules.filter(day_of_week=day_of_week).first()
            if schedule:
                return schedule
            # Если индивидуального расписания нет, ищем в шаблоне
            if self.schedule_template:
                template_schedule = self.schedule_template.items.filter(day_of_week=day_of_week).first()
                return template_schedule
            return None

        # Полное расписание, сгруппированное по дням
        schedules = self.schedules.order_by('order')
        if not schedules.exists() and self.schedule_template:
            schedules = self.schedule_template.items.order_by('order')
        return schedules

    def get_today_schedule(self):
        """Получить расписание на сегодня."""
        from datetime import datetime
        today = datetime.now().date()
        return self.get_schedule(specific_date=today)


# Модель шаблона расписания
class ScheduleTemplate(models.Model):
    name = models.CharField(max_length=256, help_text=_('E.g., "Standard office hours"'))

    def __str__(self):
        return self.name


# Модель для элементов шаблона расписания
class ScheduleTemplateItem(models.Model):
    class DayOfWeek(models.TextChoices):
        MONDAY = 'MON', _('Monday')
        TUESDAY = 'TUE', _('Tuesday')
        WEDNESDAY = 'WED', _('Wednesday')
        THURSDAY = 'THU', _('Thursday')
        FRIDAY = 'FRI', _('Friday')
        SATURDAY = 'SAT', _('Saturday')
        SUNDAY = 'SUN', _('Sunday')

    # Порядок дней недели
    DAY_ORDER = {
        'MON': 1,  # Понедельник
        'TUE': 2,  # Вторник
        'WED': 3,  # Среда
        'THU': 4,  # Четверг
        'FRI': 5,  # Пятница
        'SAT': 6,  # Суббота
        'SUN': 7,  # Воскресенье
    }

    template = models.ForeignKey(ScheduleTemplate, on_delete=models.CASCADE, related_name='items')
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    is_closed = models.BooleanField(default=False)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    order = models.IntegerField(default=0, editable=False)  # Поле для порядка

    class Meta:
        unique_together = ('template', 'day_of_week')
        verbose_name = _('Schedule Template Item')
        verbose_name_plural = _('Schedule Template Items')
        ordering = ['order']  # Сортировка по числовому полю order

    def __str__(self):
        if self.is_closed:
            return f'{self.get_day_of_week_display()}: Closed'
        return f'{self.get_day_of_week_display()}: {self.open_time} - {self.close_time}'

    def save(self, *args, **kwargs):
        # Устанавливаем порядок на основе DAY_ORDER перед сохранением
        self.order = self.DAY_ORDER.get(self.day_of_week, 0)
        super().save(*args, **kwargs)


# Расписание филиала
class BranchSchedule(models.Model):
    class DayOfWeek(models.TextChoices):
        MONDAY = 'MON', _('Monday')
        TUESDAY = 'TUE', _('Tuesday')
        WEDNESDAY = 'WED', _('Wednesday')
        THURSDAY = 'THU', _('Thursday')
        FRIDAY = 'FRI', _('Friday')
        SATURDAY = 'SAT', _('Saturday')
        SUNDAY = 'SUN', _('Sunday')

    # Порядок дней недели
    DAY_ORDER = {
        'MON': 1,
        'TUE': 2,
        'WED': 3,
        'THU': 4,
        'FRI': 5,
        'SAT': 6,
        'SUN': 7,
    }

    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices)
    is_closed = models.BooleanField(default=False)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)
    order = models.IntegerField(default=0, editable=False)  # Поле для порядка

    class Meta:
        unique_together = ('branch', 'day_of_week')
        verbose_name = _('Branch Schedule')
        verbose_name_plural = _('Branch Schedules')
        ordering = ['order']  # Сортировка по числовому полю order

    def __str__(self):
        if self.is_closed:
            return f'{self.get_day_of_week_display()}: Closed'
        return f'{self.get_day_of_week_display()}: {self.open_time} - {self.close_time}'

    def save(self, *args, **kwargs):
        # Устанавливаем порядок на основе DAY_ORDER перед сохранением
        self.order = self.DAY_ORDER.get(self.day_of_week, 0)
        super().save(*args, **kwargs)


# Исключения в расписании
class BranchScheduleException(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='schedule_exceptions')
    date = models.DateField()
    is_closed = models.BooleanField(default=False)
    open_time = models.TimeField(null=True, blank=True)
    close_time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('branch', 'date')
        verbose_name = _('Branch Schedule Exception')
        verbose_name_plural = _('Branch Schedule Exceptions')

    def __str__(self):
        if self.is_closed:
            return f'{self.date}: Closed'
        return f'{self.date}: {self.open_time} - {self.close_time}'


class Color(models.Model):
    vendor_code = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    rgb_code = models.CharField(max_length=50)

    def __str__(self):
        return f'{self.vendor_code}, {self.name}'


class Volume(models.Model):
    size = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f'{self.size}'


class BindingSubstance(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return f'{self.name} основа'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='category/images/', blank=True)

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=256)
    categories = models.ManyToManyField(Category, related_name='product_types', blank=True)

    def __str__(self):
        return f'{self.name}'


# Product model
class Product(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, null=True, blank=True)
    usage = models.CharField(max_length=256, null=True, blank=True)
    binding_substance = models.ForeignKey(BindingSubstance, on_delete=models.CASCADE, null=True, blank=True)
    dry_residue = models.CharField(max_length=256, null=True, blank=True)
    density = models.CharField(max_length=256, null=True, blank=True)
    drying_time = models.CharField(max_length=256, null=True, blank=True)
    consumption = models.CharField(max_length=256, null=True, blank=True)
    solvent = models.CharField(max_length=256, null=True, blank=True)
    working_tools = models.CharField(max_length=256, null=True, blank=True)
    tool_cleaning = models.CharField(max_length=256, null=True, blank=True)
    storage = models.CharField(max_length=256, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_discounted = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    is_in_stock = models.BooleanField(default=False)
    related_products = models.ManyToManyField('self', blank=True)
    similar_products = models.ManyToManyField('self', blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    stocks = models.ManyToManyField(Branch, through='ProductStock', related_name='product_stocks')

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/images/')

    def __str__(self):
        return f"Image for {self.product.name}"


class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, null=True, blank=True)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('product', 'branch', 'volume', 'color')

    def __str__(self):
        return f'{self.product} - {self.branch} - {self.volume} - {self.color} - {self.quantity}'


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


class SalesLeaders(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_leaders')

    def __str__(self):
        return f'{self.product}'


class RecommendedProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommended_products')

    def __str__(self):
        return f'{self.product}'


class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage'),  # Знижка у відсотках
        ('amount', 'Amount'),  # Знижка на певну суму
    ]

    code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_usage_count = models.PositiveIntegerField(null=True, blank=True)
    expiry_date = models.DateTimeField(null=True, blank=True)
    usage_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.code:  # Генеруємо код, якщо поле пусте
            self.code = self.generate_random_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_random_code(length=16):
        """
        Генерує випадковий код з вказаною кількістю символів.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choices(characters, k=length))

    def __str__(self):
        discount_info = f"{self.discount_value}% off" if self.discount_type == 'percentage' else f"${self.discount_value} off"
        return f"{self.code} - {discount_info}"


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

    def __str__(self):
        return f'{self.name}'


class ShipmentMethod(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='shipment_methods/images/')

    def __str__(self):
        return f'{self.name}'


class PaymentMethod(models.Model):
    name = models.CharField(max_length=256)
    image = models.ImageField(upload_to='payment_methods/images/')

    def __str__(self):
        return f'{self.name}'


# Промежуточная модель для связи Order и Product с количеством
class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)  # Количество товара в заказе

    class Meta:
        unique_together = ('order', 'product')  # Гарантируем уникальность комбинации order + product

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"


# Order model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    products = models.ManyToManyField(Product, through='OrderProduct')
    name = models.CharField(max_length=256)
    phone = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=256, blank=True, null=True)
    shipment_method = models.ForeignKey(ShipmentMethod, on_delete=models.CASCADE)
    order_place = models.ForeignKey(Branch, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    comment = models.TextField(blank=True, null=True)
    goods_cost = models.DecimalField(max_digits=20, decimal_places=2)
    shipment_cost = models.DecimalField(max_digits=10, decimal_places=2)
    promo_applied = models.BooleanField(default=False)
    promo = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='promo_code', blank=True, null=True)
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.id}'


# Favorite products model
class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


# Product comparison model
class ProductComparison(models.Model):
    list_number = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)


def rand_slug():
    return ''.join(choice(string.ascii_letters + string.digits) for _ in range(12))


def rand_title_chars(value):
    return ''.join(choice(value) for _ in range(int(len(value) / 2)))


# News category model
class NewsCategory(models.Model):
    name = models.CharField(max_length=256, verbose_name="Название категории")
    slug = models.SlugField(max_length=256, unique=True, blank=True, verbose_name="URL-имя")
    image = models.FileField(upload_to='news_category/images/', blank=True, null=True, verbose_name="Иконка категории")

    class Meta:
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        update_slug = False
        if not self.slug:
            update_slug = True
            print('no slug')
        elif self.pk:
            try:
                old_instance = NewsCategory.objects.get(pk=self.pk)
                if old_instance.name != self.name:
                    update_slug = True
                    print('name changed')
            except NewsCategory.DoesNotExist:
                update_slug = True

        if update_slug:
            print(f"self.name: {self.name}")
            self.slug = slugify(unidecode(self.name))
            print(f"slugified: {self.slug}")

        super().save(*args, **kwargs)


# News model
class News(models.Model):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    main_image = models.ImageField(upload_to='news/main_images/', verbose_name="Главное изображение")
    category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, verbose_name="Категория")
    date_published = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")
    slug = models.SlugField(max_length=256, unique=True, blank=True, verbose_name="URL-имя")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-date_published']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        update_slug = False
        if not self.slug:
            update_slug = True
        elif self.pk:
            try:
                old_instance = NewsCategory.objects.get(pk=self.pk)
                if old_instance.title != self.title:
                    update_slug = True
            except NewsCategory.DoesNotExist:
                update_slug = True

        if update_slug:
            print(f"self.name: {self.title}")
            self.slug = slugify(unidecode(self.title))
            print(f"slugified: {self.title}")

        super().save(*args, **kwargs)


# News ContentBlock model
class ContentBlock(models.Model):
    CONTENT_TYPES = (
        ('paragraph', 'Абзац'),
        ('subheader', 'Подзаголовок'),
        ('image', 'Изображение'),
    )

    news = models.ForeignKey(News, related_name='content_blocks', on_delete=models.CASCADE, verbose_name="Новость")
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, verbose_name="Тип контента")
    text = models.TextField(blank=True, null=True, verbose_name="Текст")
    image = models.ImageField(upload_to='news/content_images/', blank=True, null=True, verbose_name="Изображение")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")

    class Meta:
        verbose_name = "Блок контента"
        verbose_name_plural = "Блоки контента"
        ordering = ['order']

    def __str__(self):
        return f"{self.content_type} для {self.news.title}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class MainPageSections(models.Model):
    name = models.ForeignKey(Category, on_delete=models.CASCADE)


class MainPageBanner(models.Model):
    image = models.ImageField(upload_to='main_page/images/')
    description = models.TextField()
    is_used = models.BooleanField(default=False)


class ErrorMessages(models.Model):
    name = models.CharField(verbose_name=_('error`s short name'), max_length=100, unique=True)
    message = models.CharField(verbose_name=_('error`s full text'), max_length=255)


class InfoMessages(models.Model):
    name = models.CharField(verbose_name=_('message`s short name'), max_length=100, unique=True)
    message = models.CharField(verbose_name=_('message`s full text'), max_length=255)
