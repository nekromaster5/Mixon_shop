import json
from decimal import Decimal
from urllib.parse import unquote

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# Existing import statements
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
import math

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.db.models import F, Case, When, Value, DecimalField
from django.db.models.functions import Coalesce

from .admin import ProductImageInline
from .forms import UserLoginForm
from .models import Product, Review, RecommendedProducts, SalesLeaders, City, Branch, ErrorMessages, PromoCode, Order, \
    ShipmentMethod, PaymentMethod, OrderStatus, OrderProduct, Category, BindingSubstance, ProductType, Volume, \
    ProductStock


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Вычисляем рейтинг
    # Округляем рейтинг до ближайшего 0.5 в большую сторону
    rounded_rating = math.ceil(product.average_rating * 2) / 2
    full_stars = int(rounded_rating)  # целое число полных звезд
    half_star = 1 if (rounded_rating - full_stars) == 0.5 else 0
    empty_stars = 5 - full_stars - half_star

    # Формируем список звезд, где:
    # 'full'  - полная звезда,
    # 'half'  - половинчатая,
    # 'empty' - пустая звезда.
    star_list = ['full'] * full_stars + ['half'] * half_star + ['empty'] * empty_stars
    # Для отладки
    print("DEBUG star_list =", star_list)
    context = {
        'product': product,
        'stars': star_list,  # передаем готовый список звезд в шаблон
    }
    return render(request, 'product.html', context)


class HomePage(View):
    def get(self, request):
        recommended_products = RecommendedProducts.objects.select_related('product').all()
        sales_leaders = SalesLeaders.objects.select_related('product').all()
        novelty = Product.objects.all().filter(is_new=True)
        return render(request, 'home_page.html', {
            'recommended_products': recommended_products,
            'sales_leaders': sales_leaders,
            'novelty': novelty,
        })


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


def register(request):
    return render(request, 'register.html')


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


class UniversalPaginator:
    def __init__(self, object_list, per_page):
        self.paginator = Paginator(object_list, per_page)
        self.per_page = per_page

    def get_page(self, number):
        try:
            return self.paginator.page(number)
        except PageNotAnInteger:
            return self.paginator.page(1)
        except EmptyPage:
            return self.paginator.page(self.paginator.num_pages)

    def handle_pagination(self, request, template_name, partial_template, context_extras=None):
        print(f"Pagination request GET: {request.GET}")
        page = request.GET.get('page', 1)
        load_more = request.GET.get('load_more', 'false') == 'true'

        # Декодуємо query
        query = request.GET.get('query', '')
        if query:
            query = unquote(query)
        print(f"Decoded query: {query}")

        # Отримуємо товари
        products = self.paginator.object_list
        print(f"Filtered products count: {products.count()}")

        # Пагінація
        paginated_products = self.get_page(page)
        current_page = paginated_products.number
        total_pages = self.paginator.num_pages
        next_page = current_page + 1 if paginated_products.has_next() else None

        print(f"AJAX request: current_page={current_page}, next_page={next_page}, total_pages={total_pages}")

        # Отримуємо список сторінок для пагінації
        pages_to_display = get_pages_to_display(current_page, total_pages)

        context = {
            'products': paginated_products,
            'num_pages': total_pages,
            'pages_to_display': pages_to_display,
            'query': query,
            'page_url': request.path,
        }
        if context_extras:
            context.update(context_extras)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            new_items_html = render_to_string(partial_template, context, request=request)
            # Якщо це запит load_more, повертаємо пагінацію для поточної сторінки
            if load_more:
                context['products'] = paginated_products  # Залишаємо поточну сторінку
            else:
                # Для звичайного AJAX-запиту (наприклад, при кліку на номер сторінки) оновлюємо пагінацію
                if paginated_products.has_next():
                    context['products'] = self.get_page(current_page + 1)
                else:
                    context['products'] = paginated_products
            new_pagination_html = render_to_string('pagination_catalogue.html', context, request=request)
            print(f"Returning pagination HTML: \n{new_pagination_html[:100]}...")
            return JsonResponse({
                'new_items_html': new_items_html,
                'new_pagination_html': new_pagination_html,
            })

        return render(request, template_name, context)


class CataloguePage(View):
    def get(self, request):
        print("Request GET:", request.GET)
        product_type_ids = request.GET.getlist('type')
        binding_substance_id = request.GET.get('binding_substance')
        volume_ids = request.GET.getlist('volume')
        is_discounted = request.GET.get('is_discounted', 'false') == 'true'
        is_new = request.GET.get('is_new', 'false') == 'true'
        is_in_stock = request.GET.get('is_in_stock', 'false') == 'true'
        sort_type = request.GET.get('sort_type', 'popularity')

        print(f"product_type_ids: {product_type_ids}")
        print(f"binding_substance_id: {binding_substance_id}")
        print(f"volume_ids: {volume_ids}")
        print(f"is_discounted: {is_discounted}, is_new: {is_new}, is_in_stock: {is_in_stock}")
        print(f"sort_type: {sort_type}")

        products = Product.objects.prefetch_related('images').all()

        # Фільтрація
        if product_type_ids:
            products = products.filter(type__id__in=product_type_ids)
        if binding_substance_id:
            products = products.filter(binding_substance__id=binding_substance_id)
        if volume_ids:
            product_ids_with_volumes = ProductStock.objects.filter(
                volume__id__in=volume_ids
            ).values_list('product__id', flat=True).distinct()
            products = products.filter(id__in=product_ids_with_volumes)
        if is_discounted:
            products = products.filter(is_discounted=True)
        if is_new:
            products = products.filter(is_new=True)
        if is_in_stock:
            products = products.filter(is_in_stock=True)

        # Сортування
        if sort_type == 'popularity':
            products = products.order_by('-average_rating')
        elif sort_type == 'price':
            products = products.annotate(
                effective_price=Coalesce(
                    Case(
                        When(is_discounted=True, then=F('discount_price')),
                        default=F('price'),
                        output_field=DecimalField()
                    ),
                    Value(0.0, output_field=DecimalField())
                )
            ).order_by('-effective_price')
        elif sort_type == 'name':
            products = products.order_by('name')

        product_types = ProductType.objects.all()
        binding_substances = BindingSubstance.objects.all()
        product_volumes = Volume.objects.all()

        print(f"Product types count: {product_types.count()}")
        print(f"Binding substances count: {binding_substances.count()}")
        print(f"Product volumes count: {product_volumes.count()}")

        print(f"Catalogue products count: {products.count()}")
        paginator = UniversalPaginator(products, per_page=1)
        page = request.GET.get('page', 1)
        paginated_products = paginator.get_page(page)
        print(f"Has next page: {paginated_products.has_next()}")

        context_extras = {
            'product_type': None,
            'page_type': 'catalogue',
            'product_types': product_types,
            'binding_substances': binding_substances,
            'product_volumes': product_volumes,
            'selected_types': product_type_ids,
            'selected_binding_substance': binding_substance_id,
            'selected_volumes': volume_ids,
            'is_discounted': is_discounted,
            'is_new': is_new,
            'is_in_stock': is_in_stock,
            'sort_type': sort_type,
        }

        response = paginator.handle_pagination(
            request,
            template_name='catalogue.html',
            partial_template='partials/products_partial.html',
            context_extras=context_extras
        )
        return response


class SearchPage(View):
    def get(self, request):
        query = request.GET.get('query', '').strip()
        if query:
            products_list = Product.objects.filter(name__icontains=query).prefetch_related('images').order_by('name')
        else:
            products_list = Product.objects.prefetch_related('images').all().order_by('name')

        paginator = UniversalPaginator(products_list, per_page=1)
        page = request.GET.get('page', 1)
        paginated_products = paginator.get_page(page)
        print(f"Search products count: {products_list.count()}")
        print(f"Has next page: {paginated_products.has_next()}")
        return paginator.handle_pagination(
            request,
            template_name='search.html',
            partial_template='partials/products_partial.html',
            context_extras={'query': query, 'page_type': 'search'}  # Додаємо page_type
        )

    def post(self, request):
        query = request.POST.get('query', '')
        return redirect(f'/search/?query={query}&page=1' if query else '/search/?page=1')


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
        products = Product.objects.prefetch_related('images').filter(id__in=[1, 2])
        total_price = sum(
            product.discount_price if product.is_discounted and product.discount_price is not None else product.price
            for product in products
        )
        cities = City.objects.all()

        return render(request, 'checkout.html', {
            'products': products,
            'total_price': total_price,
            'cities': cities,
        })

    def post(self, request):
        # Получаем данные из AJAX-запроса
        data = json.loads(request.body)
        product_counts = data.get('products', {})

        # Получаем товары из базы данных
        products = Product.objects.filter(id__in=product_counts.keys())

        # Пересчитываем общую сумму
        total_price = 0
        for product in products:
            count = int(product_counts.get(str(product.id), 1))
            price = product.discount_price if product.is_discounted and product.discount_price is not None else product.price
            total_price += float(price) * count  # Приводим price к float

        # Возвращаем результат как JSON, убедившись, что total_price — это число
        return JsonResponse({'total_price': float(total_price)})  # Приводим к float


def get_branches(request):
    city_id = request.GET.get("city_id")
    branches = Branch.objects.filter(city_id=city_id)

    html = render(request, "partials/branches_list-checkout.html", {"branches": branches}).content.decode("utf-8")
    return JsonResponse({"html": html})


def apply_promo_code(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        if not code:
            return JsonResponse({"success": False, "error": "Введите промокод."}, status=400)

        applied_promo = request.session.get('applied_promo_code')
        if applied_promo == code:
            return JsonResponse({"success": False, "error": "Этот промокод уже применен."}, status=400)

        try:
            promo = PromoCode.objects.get(code=code)

            if promo.expiry_date and promo.expiry_date < now():
                return JsonResponse({"success": False, "error": "Срок действия промокода истек."}, status=400)

            if promo.max_usage_count is not None and promo.usage_count >= promo.max_usage_count:
                return JsonResponse(
                    {"success": False, "error": "Этот промокод уже использован максимальное количество раз."},
                    status=400)

            discount = promo.discount_value if promo.discount_type == "amount" else f"{promo.discount_value}%"

            promo.usage_count += 1
            promo.save()

            # Сохраняем промокод в сессии
            request.session['applied_promo_code'] = code
            request.session['discount'] = {
                'type': promo.discount_type,
                'value': float(promo.discount_value)
            }
            request.session.modified = True  # Гарантируем сохранение сессии
            print(f"Сохранен промокод в сессии: {request.session['applied_promo_code']}")  # Отладочный вывод

            return JsonResponse({"success": True, "discount": discount})

        except PromoCode.DoesNotExist:
            return JsonResponse({"success": False, "error": "Неверный промокод."}, status=400)

    return JsonResponse({"success": False, "error": "Неверный метод запроса."}, status=405)


def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Проверяем обязательные поля
        required_fields = ['name', 'shipment_method', 'order_place', 'payment_method', 'goods_cost', 'shipment_cost']
        for field in required_fields:
            if field not in data or data[field] is None:
                return JsonResponse({"success": False, "error": f"Поле '{field}' обязательно для заполнения."},
                                    status=400)

        # Проверяем, что хотя бы одно из полей phone или email заполнено
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        if not phone and not email:
            return JsonResponse({"success": False, "error": "Необходимо указать хотя бы телефон или email для связи."},
                                status=400)

        try:
            # Получаем данные
            name = data.get('name')
            shipment_method_id = int(data.get('shipment_method'))
            order_place_id = int(data.get('order_place'))
            payment_method_id = int(data.get('payment_method'))
            comment = data.get('comment', '')
            goods_cost = float(data.get('goods_cost'))
            shipment_cost = float(data.get('shipment_cost'))
            product_counts = data.get('products', {})  # Формат: {product_id: quantity}
            promo_code = data.get('promo_code')

            # Получаем объекты из базы данных
            shipment_method = ShipmentMethod.objects.get(id=shipment_method_id)
            order_place = Branch.objects.get(id=order_place_id)
            payment_method = PaymentMethod.objects.get(id=payment_method_id)
            status = OrderStatus.objects.get(id=1)  # Статус "Заказ принят"

            # Получаем продукты
            products = Product.objects.filter(id__in=product_counts.keys())
            if not products:
                return JsonResponse({"success": False, "error": "Не выбрано ни одного товара."}, status=400)

            # Проверяем промокод
            promo_applied = False
            promo = None
            if promo_code:
                try:
                    promo = PromoCode.objects.get(code=promo_code)
                    promo_applied = True
                    print(f"Промокод найден: {promo.code}, promo_applied: {promo_applied}")
                except PromoCode.DoesNotExist:
                    print(f"Промокод {promo_code} не найден в базе данных")
                    pass

            # Создаем заказ
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                name=name,
                phone=phone,
                email=email,
                shipment_method=shipment_method,
                order_place=order_place,
                payment_method=payment_method,
                comment=comment,
                goods_cost=goods_cost,
                shipment_cost=shipment_cost,
                promo_applied=promo_applied,
                promo=promo,
                status=status,
            )

            # Добавляем продукты в заказ с количеством через OrderProduct
            for product_id, quantity in product_counts.items():
                product = Product.objects.get(id=int(product_id))
                OrderProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=int(quantity)
                )

            # Очищаем сессию (если она используется)
            if 'applied_promo_code' in request.session:
                del request.session['applied_promo_code']
            if 'discount' in request.session:
                del request.session['discount']

            return JsonResponse({"success": True, "message": "Заказ успешно создан!"})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Неверный метод запроса."}, status=405)


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


def branch_list(request):
    """
    Отображает список всех филиалов (Branch),
    включая связанные города и номера телефонов.
    """
    branches = Branch.objects.select_related('city').prefetch_related('phone_numbers').all()
    # select_related('city') - подгрузит связанную запись City
    # prefetch_related('phone_numbers') - подгрузит связанные номера телефонов

    context = {
        'branches': branches,
    }
    return render(request, 'locations/branch_list.html', context)


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
                messages.error(request, ErrorMessages.objects.get(name='invalid_auth').message)
    else:
        form = UserLoginForm()
    return render(request, 'your_app/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


def get_session_cart(request):
    """
    Возвращает словарь корзины из сессии.
    Если корзины нет, создаёт пустую.
    """
    cart = request.session.get(settings.CART_SESSION_ID)
    if not cart:
        cart = request.session[settings.CART_SESSION_ID] = {}
    return cart


def cart_add(request, product_id):
    cart = get_session_cart(request)
    product = get_object_or_404(Product, id=product_id)
    product_id_str = str(product.id)

    if product_id_str not in cart:
        cart[product_id_str] = {'quantity': 0, 'price': str(product.price)}
    # Добавляем 1 штуку товара, можно расширить логику для указания количества
    cart[product_id_str]['quantity'] += 1
    request.session.modified = True
    return redirect('cart_detail')


def cart_remove(request, product_id):
    cart = get_session_cart(request)
    product_id_str = str(product_id)
    if product_id_str in cart:
        del cart[product_id_str]
        request.session.modified = True
    return redirect('cart_detail')


def cart_detail(request):
    cart = get_session_cart(request)
    cart_items = []
    total_price = 0
    product_ids = cart.keys()
    products = Product.objects.filter(id__in=product_ids)

    for product in products:
        item = cart[str(product.id)]
        item['product'] = product
        item['total_price'] = Decimal(item['price']) * item['quantity']
        total_price += item['total_price']
        cart_items.append(item)

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'cart/detail.html', context)


@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Получаем данные из POST-запроса
    rating = request.POST.get('rating', '0')
    pros = request.POST.get('pros', '')
    cons = request.POST.get('cons', '')
    review_text = request.POST.get('review_text', '')
    reviewer_name = request.POST.get('name', '')
    phone = request.POST.get('phone', '')

    try:
        rating_int = int(round(float(rating)))
    except ValueError:
        rating_int = 0

    # Здесь user = None, так как авторизация отсутствует
    Review.objects.create(
        product=product,
        user=None,  # или можно установить специального анонимного пользователя, если требуется
        reviewer_name=reviewer_name,
        phone=phone,
        rating=rating_int,
        pros=pros,
        cons=cons,
        review_text=review_text
    )

    # Перенаправляем пользователя обратно на страницу продукта
    return render(request, 'product.html', context)
