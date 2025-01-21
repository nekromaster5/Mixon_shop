from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.shortcuts import redirect
# Existing import statements
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.views import View
from .models import Product
from django.shortcuts import render, redirect

class HomePage(View):
    def get(self, request):
        products = Product.objects.prefetch_related('images').all()
        return render(request, 'home_page.html', {'products': products})


class ProductPage(View):
    def get(self, request, product_id):
        # Получаем продукт по его ID
        product = get_object_or_404(Product, id=product_id)

        # Получаем изображения продукта через related_name 'images'
        images = product.images.all()  # Все изображения продукта

        return render(request, 'product.html', {
            'product': product,
            'images': images,
        })


class CataloguePage(View):
    def get(self, request):
        products = Product.objects.prefetch_related('images').all()
        return render(request, 'catalogue.html', {'products': products})
from django.shortcuts import render

def register(request):
    return render(request, 'register.html')

from django.shortcuts import render

def activate(request):
    # Логика для активации аккаунта
    return render(request, 'activation_success.html')

def get_pages_to_display(current_page, total_pages):
    """
    Повертає список, наприклад: [2,3,4,5,'...',13]
    за принципом:
      - Якщо total_pages <= 6: показати всі (1..total_pages).
      - Якщо (current_page + 5) < total_pages:
          -> [current_page, current_page+1, current_page+2, current_page+3, '...', total_pages]
      - Інакше (ми «близько» до кінця): показати останні 6 сторінок [total_pages-5..total_pages].
    """
    current_page = int(current_page)
    total_pages = int(total_pages)

    if total_pages <= 6:
        # Всі сторінки від 1 до total_pages
        return list(range(1, total_pages + 1))

    # Якщо ще далеко до кінця: перший кубик = поточна сторінка
    # показуємо 4 сторінки підряд (current_page.. +3), потім '...' і останню
    if current_page + 5 < total_pages:
        return list(range(current_page, current_page + 4)) + ['...', total_pages]
    else:
        # «Близько» до кінця — показуємо останні 6 сторінок
        start = total_pages - 5
        return list(range(start, total_pages + 1))


class SearchPage(View):
    def get(self, request):
        query = request.GET.get('query', '').strip()
        # Поточна «офіційна» сторінка, з якої формується view
        page = request.GET.get('page', 1)

        if query:
            products_list = Product.objects.filter(name__icontains=query).prefetch_related('images')
        else:
            products_list = Product.objects.prefetch_related('images').all()

        paginator = Paginator(products_list, 1)  # Приклад: 2 товари на сторінку
        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        # Список сторінок, які треба відобразити у пагінації (з урахуванням «…»)
        pages_to_display = get_pages_to_display(products.number, paginator.num_pages)

        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        load_more = request.GET.get('load_more')  # параметр для "Показать ещё"

        if is_ajax and load_more:
            # Логіка «показати наступну сторінку» (тобто products.number + 1)
            next_page_num = products.number + 1
            if next_page_num <= paginator.num_pages:
                next_page = paginator.page(next_page_num)
                # HTML нового "шматка" товарів
                new_items_html = render_to_string('products_partial.html', {
                    'products': next_page
                }, request=request)

                # Переформовуємо пагінацію так, ніби тепер користувач «знаходиться» на next_page
                new_pages_to_display = get_pages_to_display(next_page.number, paginator.num_pages)
                # Рендеримо (наприклад) окремий шаблон з pagination чи навіть той самий 'search.html'
                # але зазвичай краще зробити окремий "pagination_partial.html":
                new_pagination_html = render_to_string('pagination_partial.html', {
                    'products': next_page,
                    'query': query,
                    'pages_to_display': new_pages_to_display,
                    'num_pages': paginator.num_pages
                }, request=request)

                return JsonResponse({
                    'new_items_html': new_items_html,
                    'new_pagination_html': new_pagination_html
                })
            else:
                # Вже немає наступної сторінки — можна повернути щось, щоб приховати кнопку "Показать ещё"
                return JsonResponse({
                    'new_items_html': '',
                    'new_pagination_html': ''
                })

        # Якщо не AJAX або не натиснута "Показать ещё", рендеримо звичайну сторінку
        context = {
            'products': products,
            'query': query,
            'page': products.number,
            'num_pages': paginator.num_pages,
            'pages_to_display': pages_to_display
        }
        return render(request, 'search.html', context)

    def post(self, request):
        query = request.POST.get('query', '')
        # Відправляємо на сторінку 1 пошуку
        if query:
            return redirect(f'/search/?query={query}&page=1')
        else:
            return redirect(f'/search/?page=1')

def home(request):
    # Продукты-лидеры продаж
    top_selling_products = Product.objects.filter(is_in_stock=True).order_by('-average_rating')[:5]
    
    # Новинки
    new_products = Product.objects.filter(is_new=True, is_in_stock=True).order_by('-id')[:5]
    
    # Рекомендуемые товары
    recommended_products = Product.objects.filter(is_in_stock=True).order_by('-id')[:5]
    
    return render(request, 'home_page.html', {
        'top_selling_products': top_selling_products,
        'new_products': new_products,
        'recommended_products': recommended_products,
    })
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

 

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = UserLoginForm()
    return render(request, 'your_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')