from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    Region, UserProfile, PhoneNumber, Branch, Product, Review,
    OrderStatus, Order, FavoriteProduct, ProductComparison,
    NewsCategory, News, ErrorMessages, InfoMessages, City, ProductStock, Volume, Color, ProductImage, BindingSubstance,
    ProductType, PromoCode, SalesLeaders, RecommendedProducts, MainPageSections, MainPageBanner, Category, OrderProduct,
)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'city', 'region')
    search_fields = ('user__username', 'phone', 'company', 'city')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profiles'
    fk_name = 'user'


# Кастомный UserAdmin
class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('user_info', 'email', 'phone', 'is_staff')
    list_select_related = ('userprofile',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

    @staticmethod
    def phone(instance):
        return instance.userprofile.phone

    @staticmethod
    def user_info(instance):
        return f'{instance.last_name} {instance.first_name} {instance.username}'

    user_info.short_description = 'User Info'


# Удаляем стандартный UserAdmin
admin.site.unregister(User)

# Регистрируем User модель с кастомным UserAdmin
admin.site.register(User, CustomUserAdmin)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('city', 'address', 'working_hours')
    list_filter = ('city',)
    search_fields = ('address', 'working_hours')
    filter_horizontal = ('phone_numbers',)


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('size',)
    search_fields = ('size',)


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'name', 'rgb_code')
    search_fields = ('name',)


@admin.register(BindingSubstance)
class BindingSubstanceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'branch', 'volume', 'color', 'quantity')
    search_fields = ('product__description', 'branch__address', 'volume__size', 'color__name')
    list_filter = ('branch', 'volume', 'color')


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


# Inline для OrderProduct
class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 1  # Показывать одну пустую строку для добавления нового товара
    # Убираем readonly_fields и can_delete, чтобы можно было редактировать
    # readonly_fields = ('product', 'quantity')  # Удаляем
    # can_delete = False  # Удаляем


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'is_new', 'is_discounted', 'is_in_stock', 'average_rating')
    search_fields = ('name', 'average_rating')
    inlines = [ProductImageInline]
    list_filter = ('category', 'is_discounted', 'is_new', 'is_in_stock')
    filter_horizontal = ('related_products', 'similar_products')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Отображаем имя категории
    search_fields = ('name',)  # Позволяем искать по имени
    list_filter = ()  # Фильтры не нужны, но можно добавить, если потребуется


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image')


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'max_usage_count', 'usage_count', 'expiry_date')
    list_filter = ('discount_type', 'expiry_date')
    search_fields = ('code',)
    readonly_fields = ('usage_count',)
    fieldsets = (
        (None, {
            'fields': ('code', 'discount_type', 'discount_value')
        }),
        ('Restrictions', {
            'fields': ('max_usage_count', 'expiry_date', 'usage_count')
        }),
    )


@admin.register(SalesLeaders)
class SalesLeadersAdmin(admin.ModelAdmin):
    list_display = ('product',)
    search_fields = ('product__name',)
    autocomplete_fields = ('product',)


@admin.register(RecommendedProducts)
class RecommendedProductsAdmin(admin.ModelAdmin):
    list_display = ('product',)
    search_fields = ('product__name',)
    autocomplete_fields = ('product',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating')
    search_fields = ('product__description', 'user__username', 'review_text')
    list_filter = ('rating',)


@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'phone', 'email')
    inlines = [OrderProductInline]


@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__description')


@admin.register(ProductComparison)
class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    filter_horizontal = ('products',)


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_published')
    search_fields = ('title', 'text')
    list_filter = ('category', 'date_published')


@admin.register(MainPageSections)
class MainPageSectionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_used')
    list_filter = ('is_used',)
    search_fields = ('name',)


@admin.register(MainPageBanner)
class MainPageBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'description', 'is_used')
    list_filter = ('is_used',)
    search_fields = ('description',)


@admin.register(ErrorMessages)
class ErrorMessagesAdmin(admin.ModelAdmin):
    list_display = ('message',)
    search_fields = ('message',)


@admin.register(InfoMessages)
class InfoMessagesAdmin(admin.ModelAdmin):
    list_display = ('message',)
    search_fields = ('message',)
