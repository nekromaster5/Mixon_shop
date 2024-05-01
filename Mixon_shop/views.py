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
    def get(self, request, *args, **kwargs):
        return render(request, 'error_page.html', status=404)


class Brands(View):
    def get(self, request):
        return render(request, 'brands.html')


class News(View):
    def get(self, request):
        return render(request, 'news.html')


class AboutCompany(View):
    def get(self, request):
        return render(request, 'about_company.html')


class Topic(View):
    def get(self, request):
        return render(request, 'topic.html')


class CheckoutPage(View):
    def get(self, request):
        return render(request, 'checkout.html')


class TestSlider(View):
    def get(self, request):
        return render(request, 'test_slider.html')


class Test(View):
    def get(self, request):
        return render(request, 'test.html')


class ShipmentPayment(View):
    def get(self, request):
        return render(request, 'shipment_and_payment.html')


class Contacts(View):
    def get(self, request):
        return render(request, 'contacts.html')
