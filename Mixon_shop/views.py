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

class Personalpage(View):
    def get(self, request):
        return render(request, 'Personal_Area.html')

class Erorpage(View):
    def get(self, request):
        return render(request, 'eror_page.html')
class Brands(View):
    def get(self, request):
        return render(request, 'brands.html')
class News(View):
    def get(self, request):
        return render(request, 'news.html')
