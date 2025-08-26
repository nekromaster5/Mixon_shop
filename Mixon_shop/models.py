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
    name = models.CharField(max_length=256, verbose_name='название')

    class Meta:
        verbose_name = "Область"
        verbose_name_plural = "Области"

    def __str__(self):
        return self.name


# UserProfile model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='')
    phone = models.CharField(max_length=18, null=True, blank=True, verbose_name='номер телефона')
    company = models.CharField(max_length=256, null=True, blank=True, verbose_name='компания')
    registration_number = models.CharField(max_length=256, null=True, blank=True, verbose_name='регистрационный номер')
    city = models.CharField(max_length=256, verbose_name='город')
    postal_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='почтовый индекс')
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, verbose_name='область')

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

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
    number = models.CharField(max_length=18, verbose_name='номер телефона')

    class Meta:
        verbose_name = "Номер телефона"
        verbose_name_plural = "Номера телефонов"

    def __str__(self):
        return self.number


# EmailAddress model
class EmailAddress(models.Model):
    address = models.EmailField(max_length=254, unique=True, verbose_name='адрес э-почты')

    class Meta:
        verbose_name = "Адрес э-почты"
        verbose_name_plural = "Адреса э-почты"

    def __str__(self):
        return self.address


class City(models.Model):
    name = models.CharField(max_length=256, verbose_name='название')

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"

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
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='город')
    address_base = models.CharField(max_length=512, verbose_name='Основной адрес', blank=True, null=True)
    address_detail = models.CharField(max_length=512, verbose_name='Уточняющий адрес', blank=True, null=True)
    address_short = models.CharField(max_length=512, verbose_name='Сокращенный адрес')
    phone_numbers = models.ManyToManyField(PhoneNumber, blank=True, verbose_name='номера телефонов')
    email = models.ManyToManyField(EmailAddress, blank=True, verbose_name='адреса э-почты')
    map_info = models.TextField(verbose_name='информация о координатах карты')
    schedule_template = models.ForeignKey(
        'ScheduleTemplate',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Раскладка расписания',
    )

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

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
    name = models.CharField(max_length=256,
                            help_text=_('Раскладка расписания, например "Стандартное расписание Одесса"'),
                            verbose_name='название раскладки')

    class Meta:
        verbose_name = "Раскладка расписания"
        verbose_name_plural = "Раскладки расписаний"

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
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices, verbose_name='день недели')
    is_closed = models.BooleanField(default=False, verbose_name='закрыто в этот день?')
    open_time = models.TimeField(null=True, blank=True, verbose_name='время открытия')
    close_time = models.TimeField(null=True, blank=True, verbose_name='время закрытия')
    order = models.IntegerField(default=0, editable=False)  # Поле для порядка

    class Meta:
        unique_together = ('template', 'day_of_week')
        verbose_name = _('Раскладка расписания')
        verbose_name_plural = _('Раскладки расписаний')
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
    day_of_week = models.CharField(max_length=3, choices=DayOfWeek.choices, verbose_name='день недели')
    is_closed = models.BooleanField(default=False, verbose_name='закрыто в этот день?')
    open_time = models.TimeField(null=True, blank=True, verbose_name='время открытия')
    close_time = models.TimeField(null=True, blank=True, verbose_name='время закрытия')
    order = models.IntegerField(default=0, editable=False)  # Поле для порядка

    class Meta:
        unique_together = ('branch', 'day_of_week')
        verbose_name = _('Расписание филиала')
        verbose_name_plural = _('Расписание филиалов')
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
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='schedule_exceptions',
                               verbose_name='филиал')
    date = models.DateField(verbose_name='дата')
    is_closed = models.BooleanField(default=False, verbose_name='закрыто в этот день?')
    open_time = models.TimeField(null=True, blank=True, verbose_name='время открытия')
    close_time = models.TimeField(null=True, blank=True, verbose_name='время закрытия')

    class Meta:
        unique_together = ('branch', 'date')
        verbose_name = _('Исключение в расписании филиала')
        verbose_name_plural = _('Исключения в расписании филиалов')

    def __str__(self):
        if self.is_closed:
            return f'{self.date}: Closed'
        return f'{self.date}: {self.open_time} - {self.close_time}'


class Color(models.Model):
    vendor_code = models.CharField(max_length=50, verbose_name='артикул цвета')
    name = models.CharField(max_length=50, verbose_name='название цвета')
    rgb_code = models.CharField(max_length=50, verbose_name='цвет в формате RGB')

    class Meta:
        verbose_name = "Цвет"
        verbose_name_plural = "Цвета"

    def __str__(self):
        return f'{self.vendor_code}, {self.name}'


class Volume(models.Model):
    size = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='объём')

    class Meta:
        verbose_name = "Объём"
        verbose_name_plural = "Объёмы"

    def __str__(self):
        return f'{self.size}'


class BindingSubstance(models.Model):
    name = models.CharField(max_length=256, verbose_name='название основы')

    class Meta:
        verbose_name = "Основа"
        verbose_name_plural = "Основы"

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='название категории')
    image = models.ImageField(upload_to='category/images/', blank=True, verbose_name='логотип категории')

    class Meta:
        verbose_name = "Категория товара"
        verbose_name_plural = "Категории товаров"

    def __str__(self):
        return self.name


class ProductType(models.Model):
    name = models.CharField(max_length=256, verbose_name='вид товара')
    categories = models.ManyToManyField(Category, related_name='product_types', blank=True,
                                        verbose_name='к каким категориям относится')

    class Meta:
        verbose_name = "Тип товара"
        verbose_name_plural = "Типы товаров"

    def __str__(self):
        return f'{self.name}'


# Product model
class Product(models.Model):
    name = models.CharField(max_length=256, verbose_name='название продукта')
    description = models.TextField(null=True, blank=True, verbose_name='описание продукта')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='категория продукта')
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, null=True, blank=True, verbose_name='тип продукта')
    usage = models.CharField(max_length=256, null=True, blank=True, verbose_name='назначение продукта')
    binding_substance = models.ForeignKey(BindingSubstance, on_delete=models.CASCADE, null=True, blank=True,
                                          verbose_name='вещество основы')
    dry_residue = models.CharField(max_length=256, null=True, blank=True, verbose_name='сухой остаток')
    density = models.CharField(max_length=256, null=True, blank=True, verbose_name='плотность')
    drying_time = models.CharField(max_length=256, null=True, blank=True, verbose_name='время высыхания')
    consumption = models.CharField(max_length=256, null=True, blank=True, verbose_name='потребление')
    solvent = models.CharField(max_length=256, null=True, blank=True, verbose_name='расстворитель')
    working_tools = models.CharField(max_length=256, null=True, blank=True, verbose_name='инструменты для работы')
    tool_cleaning = models.CharField(max_length=256, null=True, blank=True, verbose_name='очистка инструмента')
    storage = models.CharField(max_length=256, null=True, blank=True, verbose_name='хранение')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='цена')
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                         verbose_name='цена со скидкой')
    is_discounted = models.BooleanField(default=False, verbose_name='скидка активна?')
    is_new = models.BooleanField(default=True, verbose_name='новинка?')
    is_in_stock = models.BooleanField(default=False, verbose_name='есть в наличии?')
    related_products = models.ManyToManyField('self', blank=True, verbose_name='покупают вместе')
    similar_products = models.ManyToManyField('self', blank=True, verbose_name='похожие продукты')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, verbose_name='средняя оценка')
    stocks = models.ManyToManyField(Branch, through='ProductStock', related_name='product_stocks',
                                    verbose_name='наличие')

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name='товар')
    image = models.ImageField(upload_to='products/images/', verbose_name='картинка')

    class Meta:
        verbose_name = "Картинка товара"
        verbose_name_plural = "Картинки товаров"

    def __str__(self):
        return f"Картинка для {self.product.name}"


class ProductStock(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='товар')
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True, verbose_name='филиал')
    volume = models.ForeignKey(Volume, on_delete=models.CASCADE, null=True, blank=True, verbose_name='объём')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True, verbose_name='цвет')
    quantity = models.PositiveIntegerField(null=True, blank=True, verbose_name='кол-во')

    class Meta:
        unique_together = ('product', 'branch', 'volume', 'color')
        verbose_name = "Наличие в магазинах"
        verbose_name_plural = "Наличие в магазинах"


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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales_leaders', verbose_name='товар')

    class Meta:
        verbose_name = "Лидер продаж"
        verbose_name_plural = "Лидеры продаж"

    def __str__(self):
        return f'{self.product}'


class RecommendedProducts(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='recommended_products',
                                verbose_name='товар')

    class Meta:
        verbose_name = "Рекомендованный товар"
        verbose_name_plural = "Рекомендованные товары"

    def __str__(self):
        return f'{self.product}'


class PromoCode(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Процент'),  # Знижка у відсотках
        ('amount', 'Число'),  # Знижка на певну суму
    ]

    code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name='код скидки',
                            help_text='Оставьте пустым для генерации кода стандартизированного вида, например "Iua4CEqQj5B0Np7y"')
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, verbose_name='тип скидки')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='размер скидки')
    max_usage_count = models.PositiveIntegerField(null=True, blank=True,
                                                  verbose_name='максимальное кол-во использований')
    expiry_date = models.DateTimeField(null=True, blank=True, verbose_name='дата когда заканчивается действие')
    usage_count = models.PositiveIntegerField(default=0, verbose_name='кол-во использований')

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

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
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE, verbose_name='товар')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    review_text = models.TextField(blank=True, null=True, verbose_name='текст отзыва')
    pros = models.TextField(blank=True, null=True, verbose_name='плюсы товара')
    cons = models.TextField(blank=True, null=True, verbose_name='минусы товара')
    rating = models.IntegerField(verbose_name='поставленная оценка')

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ('product', 'user')


# Order status model
class OrderStatus(models.Model):
    name = models.CharField(max_length=256, verbose_name='статус заказа')

    class Meta:
        verbose_name = "Статус заказа"
        verbose_name_plural = "Статусы заказов"

    def __str__(self):
        return f'{self.name}'


class ShipmentMethod(models.Model):
    name = models.CharField(max_length=256, verbose_name='метод достаки')
    image = models.ImageField(upload_to='shipment_methods/images/', verbose_name='логотип метода')

    class Meta:
        verbose_name = "Метод доставки"
        verbose_name_plural = "Методы доставки"

    def __str__(self):
        return f'{self.name}'


class PaymentMethod(models.Model):
    name = models.CharField(max_length=256, verbose_name='метод оплаты')
    image = models.ImageField(upload_to='payment_methods/images/', verbose_name='логотип метода')

    class Meta:
        verbose_name = "Метод оплаты"
        verbose_name_plural = "Методы оплаты"

    def __str__(self):
        return f'{self.name}'


# Промежуточная модель для связи Order и Product с количеством
class OrderProduct(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE, verbose_name='заказ')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='товар')
    quantity = models.PositiveIntegerField(default=1,
                                           verbose_name='кол-во товара в заказе')  # Количество товара в заказе

    class Meta:
        unique_together = ('order', 'product')  # Гарантируем уникальность комбинации order + product
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"


# Order model
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name='пользователь')
    products = models.ManyToManyField(Product, through='OrderProduct', verbose_name='товар')
    name = models.CharField(max_length=256, verbose_name='имя')
    phone = models.CharField(max_length=256, blank=True, null=True, verbose_name='телефон')
    email = models.CharField(max_length=256, blank=True, null=True, verbose_name='почта')
    shipment_method = models.ForeignKey(ShipmentMethod, on_delete=models.CASCADE, verbose_name='метод доставки')
    order_place = models.ForeignKey(Branch, on_delete=models.CASCADE, verbose_name='филиал откуда заказ')
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, verbose_name='метод оплаты')
    comment = models.TextField(blank=True, null=True, verbose_name='комментарий к заказу')
    goods_cost = models.DecimalField(max_digits=20, decimal_places=2, verbose_name='стоимость товаров')
    shipment_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='стоимость доставки')
    promo_applied = models.BooleanField(default=False, verbose_name='применен ли промокод')
    promo = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='promo_code', blank=True, null=True,
                              verbose_name='промокод')
    status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE, verbose_name='статус заказа')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f'{self.id}'


# Favorite products model
class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='товар')

    class Meta:
        verbose_name = "Товар в избранном"
        verbose_name_plural = "Товары в избранном"


# Product comparison model
class ProductComparison(models.Model):
    list_number = models.IntegerField(blank=True, null=True, verbose_name='номер сравнения')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='пользователь')
    products = models.ManyToManyField(Product, verbose_name='товар')

    class Meta:
        verbose_name = "Список сравнения"
        verbose_name_plural = "Списки сравнения"


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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart', verbose_name='пользователь')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def get_total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Корзина пользователя {self.user.username}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name='корзина')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='товар')
    quantity = models.PositiveIntegerField(default=1, verbose_name='кол-во')

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"

    def total_price(self):
        return self.quantity * self.product.price

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class MainPageSections(models.Model):
    name = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='категория')

    class Meta:
        verbose_name = "Категория товаров на главной странице"
        verbose_name_plural = "Категории товаров на главной странице"


class MainPageBanner(models.Model):
    image = models.ImageField(upload_to='main_page/images/', verbose_name='изображение банера')
    description = models.TextField(verbose_name='описание банера')
    is_used = models.BooleanField(default=False, verbose_name='должен ли сейчас отображаться')

    class Meta:
        verbose_name = "Баннер на главной странице"
        verbose_name_plural = "Баннеры на главной странице"


class ErrorMessages(models.Model):
    name = models.CharField(verbose_name=_('error`s short name'), max_length=100, unique=True)
    message = models.CharField(verbose_name=_('error`s full text'), max_length=255)

    class Meta:
        verbose_name = "Сообщение об ошибке"
        verbose_name_plural = "Сообщения об ошибке"


class InfoMessages(models.Model):
    name = models.CharField(verbose_name=_('message`s short name'), max_length=100, unique=True)
    message = models.CharField(verbose_name=_('message`s full text'), max_length=255)

    class Meta:
        verbose_name = "Информационное сообщение"
        verbose_name_plural = "Информационные сообщения"
