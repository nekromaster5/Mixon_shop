"""
URL configuration for Mixon_shop project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import admin_tools
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from Mixon_shop.views import HomePage, CataloguePage, ProductPage, Brands, NewsPage, \
    AboutCompany, PersonalPage, CheckoutPage, TestSlider, Test, ErrorPage, ShipmentPayment, Contacts, \
    SearchPage, submit_review, get_branches, activate, branch_list, create_order, \
    apply_promo_code, Topic, register_view, login_view, logout_view, profile_update, change_password_view, \
    cart_add, cart_remove, cart_update, cart_detail, cart_clear, get_branch_details, manage_favorites

urlpatterns = [
    path('admin_tools/', include('admin_tools.urls')),
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),  # POST сюда — переключение uk/ru

    # продукты
    path('product/<int:product_id>/', ProductPage.as_view(), name='product'),
    path('product/<int:product_id>/submit_review/', submit_review, name='submit_review'),
    path('manage-favorites/<int:product_id>', manage_favorites, name='manage_favorites'),

    # главная и каталоги
    path('', HomePage.as_view(), name='home'),
    re_path(r'^catalogue(?:/(?P<filters>[\w/-]+))?/$', CataloguePage.as_view(), name='catalogue'),

    # поиск
    path('search/', SearchPage.as_view(), name='search'),

    # инфо-страницы
    path('brands/', Brands.as_view(), name='brands'),
    path('news/', NewsPage.as_view(), name='news_list'),
    path('topic/<slug:slug>/', Topic.as_view(), name='topic'),
    path('about_company/', AboutCompany.as_view(), name='about_company'),
    path('cabinet/', PersonalPage.as_view(), name='cabinet'),
    path('cabinet/profile/', profile_update, name='profile_update'),
    path('cabinet/password/', change_password_view, name='change_password'),
    path('checkout/', CheckoutPage.as_view(), name='checkout'),
    path('error/', ErrorPage.as_view(), name='error'),
    path('shipment&payment/', ShipmentPayment.as_view(), name='shipment_and_payment'),
    path('contacts/', Contacts.as_view(), name='contacts'),

    # филиалы
    path('branches/', branch_list, name='branch_list'),
    path('get-branches/', get_branches, name='get_branches'),
    path('get-branch-details/', get_branch_details, name='get_branch_details'),

    # аутентификация
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # корзина и заказы
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', cart_update, name='cart_update'),
    path('cart/clear/', cart_clear, name='cart_clear'),
    path('cart/', cart_detail, name='cart_detail'),
    path('apply-promo/', apply_promo_code, name='apply_promo_code'),
    path('create-order/', create_order, name='create_order'),

]

handler404 = ErrorPage.as_view()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Служебные страницы для разработки — не должны быть доступны в проде.
    urlpatterns += [
        path('slider/', TestSlider.as_view(), name='slider'),
        path('test/', Test.as_view(), name='test'),
    ]
