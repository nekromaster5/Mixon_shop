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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Mixon_shop.views import HomePage, CataloguePage, ProductPage, Brands, News, \
    Topic, AboutCompany, PersonalPage, CheckoutPage, TestSlider, Test, ErrorPage, ShipmentPayment, Contacts

urlpatterns = [
    path('admin_tools/', include('admin_tools.urls')),
    path('admin/', admin.site.urls),
    path('', HomePage.as_view(), name='home'),
    path('catalogue', CataloguePage.as_view(), name='catalogue'),
    path('product/', ProductPage.as_view(), name='product'),
    path('brands/', Brands.as_view(), name='brands'),
    path('news/', News.as_view(), name='news'),
    path('topic/', Topic.as_view(), name='topic'),
    path('about_company/', AboutCompany.as_view(), name='about_company'),
    path('cabinet/', PersonalPage.as_view(), name='cabinet'),
    path('checkout/', CheckoutPage.as_view(), name='checkout'),
    path('slider/', TestSlider.as_view(), name='slider'),
    path('test/', Test.as_view(), name='test'),
    path('error/', ErrorPage.as_view(), name='error'),
    path('shipment&payment/', ShipmentPayment.as_view(), name='shipment_and_payment'),
    path('contacts/', Contacts.as_view(), name='contacts'),
    path('product/<int:product_id>/', ProductPage.as_view(), name='product_detail'),

]

handler404 = ErrorPage.as_view()

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
