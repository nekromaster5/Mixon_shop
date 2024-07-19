from django.contrib import admin
from .models import (
    Region, UserProfile, PhoneNumber, Branch, Product, Review,
    OrderStatus, Order, FavoriteProduct, ProductComparison, 
    NewsCategory, News, ErrorMessages, InfoMessages
)

# Регистрация модели Region
admin.site.register(Region)

# Регистрация модели UserProfile
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company', 'city', 'region')
    search_fields = ('user__username', 'phone', 'company', 'city')

admin.site.register(UserProfile, UserProfileAdmin)

# Регистрация модели PhoneNumber
admin.site.register(PhoneNumber)

# Регистрация модели Branch
class BranchAdmin(admin.ModelAdmin):
    list_display = ('city', 'address', 'working_hours')
    search_fields = ('city', 'address')
    filter_horizontal = ('phone_numbers',)

admin.site.register(Branch, BranchAdmin)

# Регистрация модели Product
class ProductAdmin(admin.ModelAdmin):
    list_display = ('description', 'price', 'is_new', 'average_rating')
    search_fields = ('description', 'usage', 'binding_substance')
    list_filter = ('is_discounted', 'is_new')
    filter_horizontal = ('related_products', 'similar_products')

admin.site.register(Product, ProductAdmin)

# Регистрация модели Review
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating')
    search_fields = ('product__description', 'user__username', 'review_text')
    list_filter = ('rating',)

admin.site.register(Review, ReviewAdmin)

# Регистрация модели OrderStatus
admin.site.register(OrderStatus)

# Регистрация модели Order
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('status', 'created_at')
    filter_horizontal = ('products',)

admin.site.register(Order, OrderAdmin)

# Регистрация модели FavoriteProduct
class FavoriteProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__description')

admin.site.register(FavoriteProduct, FavoriteProductAdmin)

# Регистрация модели ProductComparison
class ProductComparisonAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    filter_horizontal = ('products',)

admin.site.register(ProductComparison, ProductComparisonAdmin)

# Регистрация модели NewsCategory
admin.site.register(NewsCategory)

# Регистрация модели News
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'date_published')
    search_fields = ('title', 'text')
    list_filter = ('category', 'date_published')

admin.site.register(News, NewsAdmin)

# Регистрация модели ErrorMessages
admin.site.register(ErrorMessages)

# Регистрация модели InfoMessages
admin.site.register(InfoMessages)
