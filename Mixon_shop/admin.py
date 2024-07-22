from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import (
    Region, UserProfile, PhoneNumber, Branch, Product, Review,
    OrderStatus, Order, FavoriteProduct, ProductComparison,
    NewsCategory, News, ErrorMessages, InfoMessages, City, ProductStock, Volume, Color
)


# Регистрация модели Region
@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Регистрация модели UserProfile
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'city', 'region')
    search_fields = ('user__username', 'phone', 'company', 'city')


# Inline модель для UserProfile
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


# Регистрация модели City
@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Регистрация модели PhoneNumber
@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('number',)
    search_fields = ('number',)


# Регистрация модели Branch
@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('city', 'address', 'working_hours')
    list_filter = ('city',)
    search_fields = ('address', 'working_hours')
    filter_horizontal = ('phone_numbers',)


# Регистрация модели Volume
@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin):
    list_display = ('size',)
    search_fields = ('size',)


# Регистрация модели Color
@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'name', 'rgb_code')
    search_fields = ('name',)


# Регистрация модели ProductStock
@admin.register(ProductStock)
class ProductStockAdmin(admin.ModelAdmin):
    list_display = ('product', 'branch', 'volume', 'color', 'quantity')
    search_fields = ('product__description', 'branch__address', 'volume__size', 'color__name')
    list_filter = ('branch', 'volume', 'color')


# Регистрация модели Product
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_new', 'is_discounted', 'average_rating')
    search_fields = ('description',)
    list_filter = ('is_discounted', 'is_new')
    filter_horizontal = ('related_products', 'similar_products')


# Регистрация модели Review
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating')
    search_fields = ('product__description', 'user__username', 'review_text')
    list_filter = ('rating',)


# Регистрация модели OrderStatus
@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Регистрация модели Order
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('status', 'created_at')
    filter_horizontal = ('products',)


# Регистрация модели FavoriteProduct
@admin.register(FavoriteProduct)
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__description')


# Регистрация модели ProductComparison
@admin.register(ProductComparison)
class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    filter_horizontal = ('products',)


# Регистрация модели NewsCategory
@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Регистрация модели News
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_published')
    search_fields = ('title', 'text')
    list_filter = ('category', 'date_published')


# Регистрация модели ErrorMessages
@admin.register(ErrorMessages)
class ErrorMessagesAdmin(admin.ModelAdmin):
    list_display = ('message',)
    search_fields = ('message',)


# Регистрация модели InfoMessages
@admin.register(InfoMessages)
class InfoMessagesAdmin(admin.ModelAdmin):
    list_display = ('message',)
    search_fields = ('message',)
