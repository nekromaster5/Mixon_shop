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
from django.contrib import admin
from django.urls import path

from Mixon_shop.views import HomePage, CataloguePage,  ProductPage,  Brands, News,  \
    New, Slider, AboutCompany,PersonalPage

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomePage.as_view(), name='home'),
    path('catalogue', CataloguePage.as_view(), name='catalogue'),
    path('product/', ProductPage.as_view(), name='product'),


    path('brands/', Brands.as_view(), name='brands'),
    path('news/', News.as_view(), name='news'),

    path('new/', New.as_view(), name='new'),
    path('Slider/', Slider.as_view()),
     path('about_company/', AboutCompany.as_view(), name='about_company'),
      path('Personal_Area/', PersonalPage.as_view(), name='Personal_Area')
]
