"""Админка магазина.

Правила, по которым она устроена (чтобы владельцу было понятно без программиста):
- у каждой модели в списке видны главные колонки, есть поиск и фильтры справа;
- формы разбиты на блоки (fieldsets), редко нужные блоки свёрнуты;
- всё, что относится к товару (фото, упаковки/цвета/остатки, характеристики), редактируется
  прямо на странице товара;
- подсказки к полям — в HELP_TEXTS у каждой админки (без миграций: правим только форму).
Группировка разделов на главной странице админки — в admin_tools/dashboard.py.
"""
from adminsortable2.admin import SortableInlineAdminMixin, SortableAdminBase
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Count
from django.utils.html import format_html
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline

from .models import (
    Region, UserProfile, PhoneNumber, Branch, Product, Review,
    OrderStatus, Order, FavoriteProduct,
    NewsCategory, News, ErrorMessages, InfoMessages, City, ProductStock, Volume, Color, ProductImage, BindingSubstance,
    ProductType, PromoCode, SalesLeaders, RecommendedProducts, MainPageSections, MainPageBanner, Category, OrderProduct,
    BranchSchedule, BranchScheduleException, ScheduleTemplateItem, ScheduleTemplate, ContentBlock, EmailAddress,
    Brand, Characteristic, ProductCharacteristic, ProductRequest, ShipmentMethod, PaymentMethod,
    ProductParameter, ProductParameterValue, ProductParameterImage, ProductTableRow,
)

admin.site.site_header = 'Mixon — управление магазином'
admin.site.site_title = 'Mixon: админка'
admin.site.index_title = 'Что будем делать?'
admin.site.empty_value_display = '—'
# Боковой список всех моделей дублирует верхнее меню по разделам и только путает
admin.site.enable_nav_sidebar = False


class HelpTextMixin:
    """Подсказки под полями формы: HELP_TEXTS = {'имя_поля': 'текст'}.
    Для переводимых полей (name_uk, name_ru) достаточно указать 'name'."""
    HELP_TEXTS = {}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        name = getattr(db_field, 'translated_field', db_field).name
        if formfield is not None and name in self.HELP_TEXTS:
            formfield.help_text = self.HELP_TEXTS[name]
        return formfield


def image_preview(file_field, height=60):
    if not file_field:
        return '—'
    return format_html('<img src="{}" style="height:{}px;max-width:160px;object-fit:contain;'
                       'border:1px solid #ddd;border-radius:4px;background:#fff">', file_field.url, height)


# ---------------------------------------------------------------- Товары

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('preview', 'image')
    readonly_fields = ('preview',)
    verbose_name = 'фото'
    verbose_name_plural = 'Фотографии (первая — главная)'

    @admin.display(description='превью')
    def preview(self, obj):
        return image_preview(obj.image)


class ProductParameterValueInline(admin.TabularInline):
    # Кнопки над таблицей на странице товара. Фото значения добавляются на его странице (ссылка «фото»)
    model = ProductParameterValue
    extra = 1
    fields = ('value', 'order', 'photos')
    readonly_fields = ('photos',)
    verbose_name = 'значение'
    verbose_name_plural = 'Значения параметра (только число, единица допишется сама)'

    @admin.display(description='фото значения')
    def photos(self, obj):
        if not obj.pk:
            return 'Сохраните товар, затем откройте значение, чтобы добавить фото'
        from django.urls import reverse
        url = reverse('admin:Mixon_shop_productparametervalue_change', args=[obj.pk])
        return format_html('{} шт. · <a href="{}">добавить/изменить фото</a>', obj.images.count(), url)


class ProductTableRowInline(TranslationTabularInline):
    model = ProductTableRow
    extra = 1
    fields = ('vendor_code', 'name', 'rgb_code', 'order')
    verbose_name = 'строка таблицы'
    verbose_name_plural = 'Строки таблицы (покупатель отмечает любые и вводит количество)'


class ProductStockInline(HelpTextMixin, admin.TabularInline):
    # Остатки по магазинам (и по упаковкам/цветам — для фильтра каталога)
    model = ProductStock
    extra = 1
    fields = ('branch', 'volume', 'color', 'quantity')
    autocomplete_fields = ('color',)
    verbose_name = 'строка наличия'
    verbose_name_plural = 'Наличие в магазинах'
    HELP_TEXTS = {
        'branch': 'Магазин, где лежит товар.',
        'volume': 'Объём упаковки (нужен для фильтра каталога). Кнопки на странице товара настраиваются выше.',
        'color': 'Можно оставить пустым, если у товара нет цветов. Начните печатать название или артикул.',
        'quantity': 'Сколько штук в этом магазине.',
    }


class ProductCharacteristicInline(TranslationTabularInline):
    model = ProductCharacteristic
    extra = 0
    fields = ('characteristic', 'value')
    verbose_name_plural = 'Характеристики (список берётся из категории товара)'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Предлагаем только характеристики из списка категории товара
        if db_field.name == 'characteristic':
            product_id = request.resolver_match.kwargs.get('object_id')
            product = Product.objects.filter(pk=product_id).first() if product_id else None
            if product:
                kwargs['queryset'] = Characteristic.objects.filter(categories=product.category)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Product)
class ProductAdmin(HelpTextMixin, TranslationAdmin):
    list_display = ('photo', 'name', 'article', 'brand', 'category', 'price', 'discount_price', 'is_discounted',
                    'is_new', 'is_in_stock')
    list_display_links = ('photo', 'name')
    list_editable = ('is_discounted', 'is_new')
    search_fields = ('name_uk', 'name_ru', 'article')
    list_filter = ('category', 'brand', 'type', 'is_in_stock', 'is_new', 'is_discounted')
    list_select_related = ('brand', 'category')
    list_per_page = 50
    autocomplete_fields = ('brand',)
    filter_horizontal = ('related_products', 'similar_products')
    readonly_fields = ('is_in_stock', 'average_rating')
    save_on_top = True
    inlines = [ProductImageInline, ProductParameterValueInline, ProductTableRowInline, ProductStockInline,
               ProductCharacteristicInline]
    # Старые фиксированные характеристики (usage, dry_residue и т.д.) заменены списками характеристик
    # по категориям, поэтому в форме их нет. binding_substance оставлен: по нему работает фильтр каталога.
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'article', ('category', 'type'), 'brand', 'binding_substance'),
        }),
        ('Цена', {
            'fields': (('price', 'discount_price'), 'is_discounted'),
        }),
        ('Отметки на сайте', {
            'fields': ('is_new', 'is_in_stock', 'average_rating'),
        }),
        ('Выбор на странице товара', {
            'fields': ('parameter', 'table_title'),
        }),
        ('Описание', {
            'fields': ('description',),
        }),
        ('Похожие и сопутствующие товары', {
            'classes': ('collapse',),
            'fields': ('similar_products', 'related_products'),
        }),
    )
    HELP_TEXTS = {
        'name': 'Название, как его увидит покупатель.',
        'article': 'Код товара у поставщика или на складе. Показывается на странице товара.',
        'category': 'Раздел каталога. От категории зависит список характеристик ниже.',
        'type': 'Вид товара внутри категории (для фильтра каталога).',
        'brand': 'Производитель. Начните печатать название.',
        'binding_substance': 'Основа (для фильтра каталога). Можно не заполнять.',
        'parameter': 'Что покупатель выбирает кнопками: «Упаковка», «Объём», «Вес»... Значения вводятся ниже. '
                     'Список параметров — в разделе «Параметры товара».',
        'table_title': 'Заголовок таблицы под кнопками, например «Цвет». Если пусто — «Цвет».',
        'price': 'Цена в гривнах.',
        'discount_price': 'Цена со скидкой. Работает, только если отмечено «скидка активна».',
        'is_discounted': 'Отметьте, чтобы показать цену со скидкой и старую цену зачёркнутой.',
        'is_new': 'Показывать значок «Новинка».',
        'is_in_stock': 'Ставится автоматически: «да», если ниже есть хотя бы одна строка наличия.',
        'average_rating': 'Считается автоматически по отзывам.',
        'similar_products': 'Показываются в блоке «Похожие товары».',
        'related_products': 'Показываются в блоке «С этим товаром покупают».',
    }

    @admin.display(description='фото')
    def photo(self, obj):
        first = obj.images.first()
        return image_preview(first.image if first else None, height=40)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('images')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        # Добавляем пустые строки для всех характеристик категории, чтобы их оставалось только заполнить
        product = form.instance
        existing = set(product.characteristic_values.values_list('characteristic_id', flat=True))
        for characteristic in Characteristic.objects.filter(categories=product.category):
            if characteristic.id not in existing:
                ProductCharacteristic.objects.create(product=product, characteristic=characteristic)


@admin.register(ProductParameter)
class ProductParameterAdmin(HelpTextMixin, TranslationAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name_uk', 'name_ru')
    HELP_TEXTS = {
        'name': 'Например «Упаковка» или «Объём». Это подпись над кнопками на странице товара.',
        'unit': 'Например «л» или «кг». В значениях админ вводит только число, единица дописывается на сайте.',
    }


class ProductParameterImageInline(admin.TabularInline):
    model = ProductParameterImage
    extra = 1
    fields = ('preview', 'image', 'order')
    readonly_fields = ('preview',)
    verbose_name = 'фото'
    verbose_name_plural = 'Фото значения (при выборе значения главное фото товара заменится на них)'

    @admin.display(description='превью')
    def preview(self, obj):
        return image_preview(obj.image)


@admin.register(ProductParameterValue)
class ProductParameterValueAdmin(admin.ModelAdmin):
    list_display = ('product', 'value', 'photos_count')
    search_fields = ('product__name_uk', 'product__name_ru')
    autocomplete_fields = ('product',)
    inlines = [ProductParameterImageInline]

    def has_module_permission(self, request):
        return False  # открывается по ссылке со страницы товара

    @admin.display(description='фото')
    def photos_count(self, obj):
        return obj.images.count()


@admin.register(Category)
class CategoryAdmin(HelpTextMixin, TranslationAdmin):
    list_display = ('logo', 'name', 'menu_section', 'products_count')
    list_display_links = ('logo', 'name')
    list_filter = ('menu_section',)
    search_fields = ('name_uk', 'name_ru')
    HELP_TEXTS = {
        'image': 'Картинка для главной страницы.',
        'menu_section': 'В каком пункте меню «Каталог товаров» показывается эта категория. '
                        'Пункты меню и их иконки фиксированные.',
    }

    @admin.display(description='логотип')
    def logo(self, obj):
        return image_preview(obj.image, height=32)

    @admin.display(description='товаров', ordering='products_total')
    def products_count(self, obj):
        return obj.products_total

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_total=Count('product'))


@admin.register(Characteristic)
class CharacteristicAdmin(HelpTextMixin, TranslationAdmin):
    list_display = ('name', 'order', 'category_list')
    list_editable = ('order',)
    list_filter = ('categories',)
    search_fields = ('name_uk', 'name_ru')
    filter_horizontal = ('categories',)
    HELP_TEXTS = {
        'categories': 'У товаров этих категорий характеристика появится в списке для заполнения.',
        'order': 'Чем меньше число, тем выше строка в таблице характеристик.',
    }

    @admin.display(description='категории')
    def category_list(self, obj):
        return ', '.join(category.name for category in obj.categories.all())

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'slug', 'order', 'products_count')
    list_display_links = ('logo_preview', 'name')
    list_editable = ('order',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='логотип')
    def logo_preview(self, obj):
        return image_preview(obj.logo, height=32)

    @admin.display(description='товаров', ordering='products_total')
    def products_count(self, obj):
        return obj.products_total

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_total=Count('products'))


@admin.register(ProductType)
class ProductTypeAdmin(TranslationAdmin):
    list_display = ('name', 'category_list')
    list_filter = ('categories',)
    search_fields = ('name_uk', 'name_ru')
    filter_horizontal = ('categories',)

    @admin.display(description='категории')
    def category_list(self, obj):
        return ', '.join(category.name for category in obj.categories.all())

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')


@admin.register(BindingSubstance)
class BindingSubstanceAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name_uk', 'name_ru')


@admin.register(Color)
class ColorAdmin(HelpTextMixin, admin.ModelAdmin):
    list_display = ('swatch', 'vendor_code', 'name', 'rgb_code')
    list_display_links = ('swatch', 'vendor_code', 'name')
    search_fields = ('name', 'vendor_code')
    HELP_TEXTS = {
        'vendor_code': 'Номер цвета по каталогу (например, RAL 9003).',
        'rgb_code': 'Цвет кружка на сайте: #RRGGBB, например #FFFFFF, или rgb(255, 255, 255).',
    }

    @admin.display(description='цвет')
    def swatch(self, obj):
        return format_html('<span style="display:inline-block;width:24px;height:24px;border-radius:50%;'
                           'border:1px solid #999;background:{}"></span>', obj.rgb_code)


@admin.register(Volume)
class VolumeAdmin(HelpTextMixin, admin.ModelAdmin):
    list_display = ('size',)
    search_fields = ('size',)
    ordering = ('size',)
    HELP_TEXTS = {'size': 'Объём упаковки в литрах, например 0.75 или 10.'}


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'branch', 'volume', 'color', 'quantity')
    list_editable = ('quantity',)
    search_fields = ('product__name_uk', 'product__name_ru', 'product__article', 'color__name',
                     'color__vendor_code')
    list_filter = ('branch', 'volume')
    list_select_related = ('product', 'branch__city', 'volume', 'color')
    autocomplete_fields = ('product', 'color')


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('preview', 'product')
    search_fields = ('product__name_uk', 'product__name_ru')
    autocomplete_fields = ('product',)

    @admin.display(description='фото')
    def preview(self, obj):
        return image_preview(obj.image, height=40)


# ---------------------------------------------------------------- Заказы и заявки

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    autocomplete_fields = ('product',)
    verbose_name_plural = 'Товары в заказе'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'name', 'phone', 'total', 'shipment_method', 'status')
    list_display_links = ('id', 'name')
    list_editable = ('status',)
    list_filter = ('status', 'shipment_method', 'payment_method', 'order_place', 'created_at')
    search_fields = ('id', 'name', 'phone', 'email')
    list_select_related = ('status', 'shipment_method')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    autocomplete_fields = ('user', 'promo')
    save_on_top = True
    inlines = [OrderProductInline]
    fieldsets = (
        ('Статус', {
            'fields': ('status', 'created_at'),
        }),
        ('Покупатель', {
            'fields': ('name', 'phone', 'email', 'user', 'comment'),
        }),
        ('Доставка и оплата', {
            'fields': ('shipment_method', 'order_place', 'payment_method'),
        }),
        ('Сумма', {
            'fields': (('goods_cost', 'shipment_cost'), ('promo_applied', 'promo')),
        }),
    )

    @admin.display(description='сумма, грн')
    def total(self, obj):
        return obj.goods_cost + obj.shipment_cost


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'kind', 'product', 'selection_short', 'name', 'phone', 'is_processed')
    list_editable = ('is_processed',)
    list_filter = ('is_processed', 'kind', 'created_at')
    search_fields = ('name', 'phone', 'product__name_uk', 'product__name_ru')
    list_select_related = ('product',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'volume', 'color')
    autocomplete_fields = ('product',)
    fields = ('is_processed', 'kind', 'created_at', 'product', 'selection', ('volume', 'color'), 'name', 'phone',
              'comment')

    @admin.display(description='что выбрано')
    def selection_short(self, obj):
        return obj.selection.replace('\n', '; ') or '—'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'display_name', 'rating', 'short_text')
    search_fields = ('product__name_uk', 'product__name_ru', 'user__username', 'reviewer_name', 'review_text')
    list_filter = ('rating',)
    list_select_related = ('product', 'user')
    autocomplete_fields = ('product', 'user')
    fieldsets = (
        (None, {'fields': ('product', 'rating')}),
        ('Автор', {
            'fields': ('user', ('reviewer_name', 'phone')),
            'description': 'Если отзыв оставлен без входа в аккаунт, пользователь пуст, а имя и телефон заполнены.',
        }),
        ('Текст', {'fields': ('review_text', 'pros', 'cons')}),
    )

    @admin.display(description='автор')
    def display_name(self, obj):
        return obj.display_name

    @admin.display(description='отзыв')
    def short_text(self, obj):
        text = obj.review_text or ''
        return text if len(text) <= 80 else text[:80] + '…'


@admin.register(PromoCode)
class PromoCodeAdmin(HelpTextMixin, admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'max_usage_count', 'usage_count', 'expiry_date')
    list_filter = ('discount_type', 'expiry_date')
    search_fields = ('code',)
    readonly_fields = ('usage_count',)
    fieldsets = (
        ('Промокод', {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Ограничения', {
            'fields': ('max_usage_count', 'expiry_date', 'usage_count')
        }),
    )
    HELP_TEXTS = {
        'discount_value': 'Для «Процент» — сколько процентов, для «Число» — сколько гривен.',
        'max_usage_count': 'Пусто — без ограничения.',
        'expiry_date': 'Пусто — бессрочно.',
    }


@admin.register(OrderStatus)
class OrderStatusAdmin(TranslationAdmin):
    list_display = ('id', 'name')
    search_fields = ('name_uk', 'name_ru')


@admin.register(ShipmentMethod)
class ShipmentMethodAdmin(TranslationAdmin):
    list_display = ('logo', 'name')
    list_display_links = ('logo', 'name')
    search_fields = ('name_uk', 'name_ru')

    @admin.display(description='логотип')
    def logo(self, obj):
        return image_preview(obj.image, height=32)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(TranslationAdmin):
    list_display = ('logo', 'name')
    list_display_links = ('logo', 'name')
    search_fields = ('name_uk', 'name_ru')

    @admin.display(description='логотип')
    def logo(self, obj):
        return image_preview(obj.image, height=32)


# ---------------------------------------------------------------- Главная страница и новости

@admin.register(MainPageBanner)
class MainPageBannerAdmin(HelpTextMixin, TranslationAdmin):
    list_display = ('preview', 'description', 'is_used')
    list_display_links = ('preview', 'description')
    list_editable = ('is_used',)
    list_filter = ('is_used',)
    search_fields = ('description_uk', 'description_ru')
    HELP_TEXTS = {'is_used': 'Снимите отметку, чтобы убрать баннер с главной, не удаляя его.'}

    @admin.display(description='баннер')
    def preview(self, obj):
        return image_preview(obj.image, height=50)


@admin.register(MainPageSections)
class MainPageSectionsAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name__name_uk', 'name__name_ru')


@admin.register(SalesLeaders)
class SalesLeadersAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_price')
    search_fields = ('product__name_uk', 'product__name_ru')
    list_select_related = ('product',)
    autocomplete_fields = ('product',)

    @admin.display(description='цена')
    def product_price(self, obj):
        return obj.product.price


@admin.register(RecommendedProducts)
class RecommendedProductsAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_price')
    search_fields = ('product__name_uk', 'product__name_ru')
    list_select_related = ('product',)
    autocomplete_fields = ('product',)

    @admin.display(description='цена')
    def product_price(self, obj):
        return obj.product.price


class ContentBlockInline(TranslationTabularInline, SortableInlineAdminMixin, admin.TabularInline):
    model = ContentBlock
    extra = 1
    fields = ('content_type', 'text', 'image', 'order')
    ordering = ['order']
    verbose_name_plural = 'Текст новости по блокам (порядок меняется перетаскиванием)'


@admin.register(News)
class NewsAdmin(SortableAdminBase, TranslationAdmin):
    list_display = ('title', 'category', 'date_published')
    list_filter = ('category', 'date_published')
    search_fields = ('title_uk', 'title_ru')
    date_hierarchy = 'date_published'
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ContentBlockInline]


@admin.register(NewsCategory)
class NewsCategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name_uk', 'name_ru')


# ---------------------------------------------------------------- Магазины

class BranchScheduleInline(admin.TabularInline):
    model = BranchSchedule
    extra = 0
    fields = ('day_of_week', 'is_closed', 'open_time', 'close_time')
    verbose_name_plural = 'Своё расписание магазина (если отличается от раскладки)'

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 7
        return 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('order')


class BranchScheduleExceptionInline(admin.TabularInline):
    model = BranchScheduleException
    extra = 0
    fields = ('date', 'is_closed', 'open_time', 'close_time')
    verbose_name_plural = 'Особые дни (праздники, переучёт)'


class ScheduleTemplateItemInline(admin.TabularInline):
    model = ScheduleTemplateItem
    extra = 0
    fields = ('day_of_week', 'is_closed', 'open_time', 'close_time')
    verbose_name = 'день'
    verbose_name_plural = 'Дни недели'

    def get_extra(self, request, obj=None, **kwargs):
        if obj is None:
            return 7
        return 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('order')


@admin.register(Branch)
class BranchAdmin(HelpTextMixin, TranslationAdmin):
    list_display = ('address_short', 'city', 'schedule_template')
    list_filter = ('city', 'schedule_template')
    search_fields = ('address_short_uk', 'address_short_ru', 'address_base_uk', 'address_base_ru',
                     'city__name_uk', 'city__name_ru')
    list_select_related = ('city', 'schedule_template')
    filter_horizontal = ('phone_numbers', 'email')
    inlines = [BranchScheduleInline, BranchScheduleExceptionInline]
    fieldsets = (
        ('Адрес', {
            'fields': ('city', 'address_short', 'address_base', 'address_detail', 'map_info'),
        }),
        ('Контакты', {
            'fields': ('phone_numbers', 'email'),
        }),
        ('Часы работы', {
            'fields': ('schedule_template',),
            'description': 'Выберите готовую раскладку расписания или заполните расписание магазина ниже.',
        }),
    )
    HELP_TEXTS = {
        'address_short': 'Короткий адрес для списков, например «ул. Бугаевская, 21».',
        'address_base': 'Полный адрес для страницы контактов.',
        'address_detail': 'Уточнение: этаж, вход, ориентир.',
        'map_info': 'Координаты для карты в виде «lat: 46.4825, lng: 30.7233» '
                    '(числа можно скопировать из Google Maps).',
    }


@admin.register(ScheduleTemplate)
class ScheduleTemplateAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [ScheduleTemplateItemInline]


@admin.register(City)
class CityAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name_uk', 'name_ru')


@admin.register(Region)
class RegionAdmin(TranslationAdmin):
    list_display = ('name',)
    search_fields = ('name_uk', 'name_ru')


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)


@admin.register(EmailAddress)
class EmailAddressAdmin(admin.ModelAdmin):
    list_display = ('address',)
    search_fields = ('address',)


# ---------------------------------------------------------------- Покупатели

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name = 'профиль покупателя'
    verbose_name_plural = 'Профиль покупателя'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('user_info', 'email', 'phone', 'is_staff', 'date_joined')
    list_select_related = ('userprofile',)
    search_fields = ('username', 'first_name', 'last_name', 'email', 'userprofile__phone')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

    @admin.display(description='телефон')
    def phone(self, obj):
        profile = getattr(obj, 'userprofile', None)
        return profile.phone if profile else None

    @admin.display(description='пользователь')
    def user_info(self, obj):
        return f'{obj.last_name} {obj.first_name} ({obj.username})'.strip()


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'city', 'region')
    search_fields = ('user__username', 'user__email', 'phone', 'company', 'city')
    list_filter = ('region',)
    list_select_related = ('user', 'region')


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__name_uk', 'product__name_ru')
    list_select_related = ('user', 'product')
    autocomplete_fields = ('user', 'product')


# ---------------------------------------------------------------- Тексты сообщений

@admin.register(ErrorMessages)
class ErrorMessagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'message')
    search_fields = ('name', 'message')


@admin.register(InfoMessages)
class InfoMessagesAdmin(admin.ModelAdmin):
    list_display = ('name', 'message')
    search_fields = ('name', 'message')
