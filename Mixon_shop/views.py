from django.shortcuts import redirect, render
from django.urls import reverse_lazy as _
from django.views import View


class HomePage(View):
    def get(self, request):
        return render(request, 'home_page.html')


class CataloguePage(View):
    def get(self, request):
        return render(request, 'catalogue.html')


class ProductPage(View):
    def get(self, request):
        return render(request, 'product.html')


class PersonalPage(View):
    def get(self, request):
        return render(request, 'Personal_Area.html')


class ErrorPage(View):
    def get(self, request):
        return render(request, 'eror_page.html')


class Brands(View):
    def get(self, request):
        return render(request, 'brands.html')


class News(View):
    def get(self, request):
        return render(request, 'news.html')


class AboutCompany(View):
    def get(self, request):
        return render(request, 'about_company.html')


class New(View):
    def get(self, request):
        return render(request, 'new.html')


class Slider(View):
    def get(self, request):
        return render(request, 'test_slider.html')
