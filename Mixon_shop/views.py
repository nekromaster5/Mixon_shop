from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import redirect
# Existing import statements
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View

from .models import Product


class HomePage(View):
    def get(self, request):
        return render(request, 'home_page.html')


class CataloguePage(View):
    def get(self, request):
        products = Product.objects.prefetch_related('images').all()
        return render(request, 'catalogue.html', {'products': products})


class SearchPage(View):
    def get(self, request):
        query = request.GET.get('query', '').strip()
        page = request.GET.get('page', 1)  # Отримуємо номер сторінки з параметра GET

        if query:
            products_list = Product.objects.filter(name__icontains=query).prefetch_related('images')
        else:
            products_list = Product.objects.prefetch_related('images').all()

        paginator = Paginator(products_list, 20)  # Пагінація по 1 продукту на сторінку
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        print(f'current page number:{products.number}')  # Друк поточного номера сторінки

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        if is_ajax:
            html = render_to_string('products_partial.html', {'products': products})
            return JsonResponse({'html': html})

        context = {
            'products': products,
            'query': query,
            'page': page,
            'num_pages': paginator.num_pages,
        }
        return render(request, 'search.html', context)

    def post(self, request):
        query = request.POST.get('query')
        return redirect(f'/search/?query={query}&page=1') if query else redirect(f'/search/?page=1')


class ProductPage(View):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        return render(request, 'product.html', {'product': product})


class PersonalPage(View):
    def get(self, request):
        return render(request, 'cabinet.html')


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
