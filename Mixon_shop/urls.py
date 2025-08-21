import admin_tools
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views  # используем только это!

urlpatterns = [
    path('admin_tools/', include('admin_tools.urls')),
    path('admin/', admin.site.urls),

    # продукты
    path('product/<int:product_id>/', views.ProductPage.as_view(), name='product'),
    path('product/<int:product_id>/submit_review/', views.submit_review, name='submit_review'),

    # главная и каталоги
    path('', views.HomePage.as_view(), name='home'),
    path('catalogue/', views.CataloguePage.as_view(), name='catalogue'),

    # поиск
    path('search/', views.SearchPage.as_view(), name='search'),
    path('search/<str:query>/page/<int:page>/', views.SearchPage.as_view(), name='search_result'),
    path('search/page/<int:page>/', views.SearchPage.as_view(), name='search_result_no_query'),

    # инфо-страницы
    path('brands/', views.Brands.as_view(), name='brands'),
    path('news/', views.News.as_view(), name='news'),
    path('topic/', views.Topic.as_view(), name='topic'),
    path('about_company/', views.AboutCompany.as_view(), name='about_company'),
    path('cabinet/', views.PersonalPage.as_view(), name='cabinet'),
    path('checkout/', views.CheckoutPage.as_view(), name='checkout'),
    path('slider/', views.TestSlider.as_view(), name='slider'),
    path('test/', views.Test.as_view(), name='test'),
    path('error/', views.ErrorPage.as_view(), name='error'),
    path('shipment&payment/', views.ShipmentPayment.as_view(), name='shipment_and_payment'),
    path('contacts/', views.Contacts.as_view(), name='contacts'),

    # филиалы
    path('branches/', views.branch_list, name='branch_list'),
    path('get-branches/', views.get_branches, name='get_branches'),

    # аутентификация
    path('register/', views.register_view, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # корзина и заказы
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('apply-promo/', views.apply_promo_code, name='apply_promo_code'),
    path('create-order/', views.create_order, name='create_order'),
]

# кастомная 404
handler404 = views.ErrorPage.as_view()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
