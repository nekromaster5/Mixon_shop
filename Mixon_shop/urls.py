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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from Mixon_shop.views import HomePage, CataloguePage, ProductPage, Brands, NewsPage, \
    AboutCompany, PersonalPage, CheckoutPage, TestSlider, Test, ErrorPage, ShipmentPayment, Contacts, \
    SearchPage, product_detail, submit_review, get_branches, activate, branch_list, create_order, \
    apply_promo_code, Topic, register_view, cart_add, cart_remove, cart_detail

urlpatterns = [
    path('admin_tools/', include('admin_tools.urls')),
    path('admin/', admin.site.urls),

    # продукты
    path('product/<int:product_id>/', ProductPage.as_view(), name='product'),
    path('product/<int:product_id>/submit_review/', submit_review, name='submit_review'),

    # главная и каталоги
    path('', HomePage.as_view(), name='home'),
    path('catalogue/', CataloguePage.as_view(), name='catalogue'),

    # поиск
    path('search/', SearchPage.as_view(), name='search'),
    path('search/<str:query>/page/<int:page>/', SearchPage.as_view(), name='search_result'),
    path('search/page/<int:page>/', SearchPage.as_view(), name='search_result_no_query'),

    # инфо-страницы
    path('brands/', Brands.as_view(), name='brands'),
    path('news/', NewsPage.as_view(), name='news_list'),
    path('topic/<slug:slug>/', Topic.as_view(), name='topic'),
    path('about_company/', AboutCompany.as_view(), name='about_company'),
    path('cabinet/', PersonalPage.as_view(), name='cabinet'),
    path('checkout/', CheckoutPage.as_view(), name='checkout'),
    path('slider/', TestSlider.as_view(), name='slider'),
    path('test/', Test.as_view(), name='test'),
    path('error/', ErrorPage.as_view(), name='error'),
    path('shipment&payment/', ShipmentPayment.as_view(), name='shipment_and_payment'),
    path('contacts/', Contacts.as_view(), name='contacts'),

    # филиалы
    path('branches/', branch_list, name='branch_list'),
    path('get-branches/', get_branches, name='get_branches'),

    # аутентификация
    path('register/', register_view, name='register'),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # корзина и заказы
    path('cart/add/<int:product_id>/', cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', cart_remove, name='cart_remove'),
    path('cart/', cart_detail, name='cart_detail'),
    path('apply-promo/', apply_promo_code, name='apply_promo_code'),
    path('create-order/', create_order, name='create_order'),

]

handler404 = ErrorPage.as_view()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
