import json
from datetime import timedelta, datetime
from urllib.parse import unquote

# Existing import statements
from django.template.loader import render_to_string
from django.utils.timezone import now
from django.utils.translation import gettext as _
from django.views import View
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
import math
from .models import MainPageSections
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse
from django.db.models import F, Case, When, Value, DecimalField, Count, Min, Max, Exists, OuterRef, Sum
from django.db.models.functions import Coalesce
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, url_has_allowed_host_and_scheme
from django.conf import settings
from unicodedata import category

from .forms import UserRegisterForm, UserLoginForm, ProfileUpdateForm
from .models import UserProfile, Region
from .forms import UserLoginForm
from .models import MainPageBanner
from .session_cart import SessionCart
from .session_compare import SessionCompare, COMPARE_MAX_PRODUCTS
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.utils.decorators import method_decorator
from .models import Product, Review, UserProfile, RecommendedProducts, SalesLeaders, City, ErrorMessages, PromoCode, \
    Order, \
    ShipmentMethod, PaymentMethod, OrderStatus, OrderProduct, BindingSubstance, ProductType, Volume, \
    ProductStock, News, NewsCategory, Branch, FavoriteProduct, Category, Brand, Color, ProductRequest

import logging

logger = logging.getLogger(__name__)


def rating_to_stars(rating):
    """Превращает числовой рейтинг (0..5) в список 'full'/'half'/'empty' —
    ровно 5 элементов — для отрисовки звёзд в шаблоне."""
    rounded_rating = math.ceil(float(rating) * 2) / 2
    full_stars = int(rounded_rating)
    half_star = 1 if (rounded_rating - full_stars) == 0.5 else 0
    empty_stars = 5 - full_stars - half_star
    return ['full'] * full_stars + ['half'] * half_star + ['empty'] * empty_stars


class ProductSelfWrapper:
    def __init__(self, product):
        self.product = product
        self.likes_count = product.likes_count
        self.comments_count = product.comments_count


def manage_favorites(request, product_id):
    if not request.user.is_authenticated:
        # AJAX-кнопке нужен понятный ответ, а не HTML страницы входа после редиректа
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "login_required"}, status=403)
        return redirect_to_login(request.get_full_path())

    product = get_object_or_404(Product,
        id=product_id if product_id else request.GET.get('product_id')
    )
    user = request.user

    favorite = FavoriteProduct.objects.filter(user=user, product=product).first()
    if favorite:
        favorite.delete()
        status = "removed"
    else:
        FavoriteProduct.objects.create(user=user, product=product)
        status = "added"

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # если вызов через AJAX — вернём JSON
        return JsonResponse({"status": status})

    return redirect(_safe_redirect_target(request))


class HomePage(View):
    def get(self, request):
        user_id = request.user.pk if request.user.is_authenticated else None
        recommended_products = RecommendedProducts.objects.select_related('product').annotate(
            likes_count=Count('product__favoriteproduct'),  # Кількість вподобайок
            comments_count=Count('product__reviews'),
            is_favorite=Exists(
                FavoriteProduct.objects.filter(
                    user_id=user_id,
                    product=OuterRef('product__id')
                )
            )
        ).all()
        sales_leaders = SalesLeaders.objects.select_related('product').annotate(
            likes_count=Count('product__favoriteproduct'),  # Кількість вподобайок
            comments_count=Count('product__reviews'),
            is_favorite=Exists(
                FavoriteProduct.objects.filter(
                    user_id=user_id,
                    product=OuterRef('product__id')
                )
            )
        ).all()
        # Новинки із кількістю вподобайок і коментарів
        novelty = Product.objects.filter(is_new=True).annotate(
            likes_count=Count('favoriteproduct'),  # Кількість вподобайок
            comments_count=Count('reviews'),
            is_favorite=Exists(
                FavoriteProduct.objects.filter(
                    user_id=user_id,
                    product=OuterRef('id')
                )
            )
        ).all()
        novelty = [ProductSelfWrapper(item) for item in novelty]

        sections = MainPageSections.objects.select_related("name").all()
        banners = MainPageBanner.objects.filter(is_used=True)
        if not banners:
            logger.warning("No active banners found for the main page.")

        for s in sections:
            logger.debug(
                f"SECTION: {s.id} -> {s.name.name} | image: {s.name.image.url if s.name.image else 'нет картинки'}")

        news = News.objects.all().order_by('-date_published')[:3]

        return render(request, 'home_page.html', {
            'recommended_products': recommended_products,
            'sales_leaders': sales_leaders,
            'novelty': novelty,
            'news': news,
            'sections': sections,
            'banners': banners,
        })


class ProductPage(View):
    def get(self, request, product_id):
        # Получаем продукт по его ID
        product = get_object_or_404(Product, id=product_id)

        # Получаем изображения продукта через related_name 'images'
        images = product.images.all()  # Все изображения продукта

        user_id = request.user.pk if request.user.is_authenticated else None

        def annotate_products(queryset):
            return queryset.prefetch_related('images').annotate(
                likes_count=Count('favoriteproduct'),
                comments_count=Count('reviews'),
                is_favorite=Exists(
                    FavoriteProduct.objects.filter(user_id=user_id, product=OuterRef('id'))
                )
            )

        related_products = [ProductSelfWrapper(p) for p in annotate_products(product.related_products.all())]
        similar_products = [ProductSelfWrapper(p) for p in annotate_products(product.similar_products.all())]

        # Цвета и объёмы берём из остатков: одна строка на цвет, кол-во суммируется по филиалам
        stocks = ProductStock.objects.filter(product=product)
        colors = (
            stocks.filter(color__isnull=False)
            .values('color__id', 'color__vendor_code', 'color__name', 'color__rgb_code')
            .annotate(total=Coalesce(Sum('quantity'), 0))
            .order_by('color__vendor_code', 'color__name')
        )
        volumes = Volume.objects.filter(productstock__product=product).distinct().order_by('size')

        # Пустые значения не выводим (значение с фолбэком на украинский проверяем уже после перевода)
        characteristics = [
            item for item in product.characteristic_values.select_related('characteristic') if item.value
        ]

        return render(request, 'product.html', {
            'product': product,
            'images': images,
            'colors': colors,
            'volumes': volumes,
            'characteristics': characteristics,
            'characteristics_left': characteristics[:(len(characteristics) + 1) // 2],
            'characteristics_right': characteristics[(len(characteristics) + 1) // 2:],
            'is_favorite': bool(user_id) and FavoriteProduct.objects.filter(user_id=user_id, product=product).exists(),
            'likes_count': product.favoriteproduct_set.count(),
            'reviews_count': product.reviews.count(),
            'stars': rating_to_stars(product.average_rating),
            # Срок доставки считается от сегодняшнего дня: в отделение до 2 дней, до квартиры до 3
            'delivery_date_branch': (now() + timedelta(days=2)).strftime('%d.%m'),
            'delivery_date_home': (now() + timedelta(days=3)).strftime('%d.%m'),
            'related_products': related_products,
            'similar_products': similar_products,
        })


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
        return list(range(1, total_pages + 1))

    # # Якщо ще далеко до кінця: перший кубик = поточна сторінка
    # # показуємо 4 сторінки підряд (current_page.. +3), потім '...' і останню
    # if current_page + 5 < total_pages:
    #     return list(range(current_page, current_page + 4)) + ['...', total_pages]
    # else:
    #     # «Близько» до кінця — показуємо останні 6 сторінок
    #     start = total_pages - 5
    #     return list(range(start, total_pages + 1))
    if current_page + 3 < total_pages:
        return [current_page, current_page + 1, current_page + 2, current_page + 3, '...', total_pages]
    else:
        start = max(1, total_pages - 5)
        return list(range(start, total_pages + 1))


class UniversalPaginator:
    def __init__(self, object_list, per_page):
        wrapped_list = [ProductSelfWrapper(item) for item in object_list]
        self.paginator = Paginator(wrapped_list, per_page)
        self.per_page = per_page
        self.has_items = len(wrapped_list) > 0  # Перевіряємо, чи є товари

    def get_page(self, number):
        try:
            return self.paginator.page(number)
        except PageNotAnInteger:
            return self.paginator.page(1)
        except EmptyPage:
            return self.paginator.page(self.paginator.num_pages)

    def handle_pagination(self, request, template_name, partial_template, context_extras=None):
        page = request.GET.get('page', '1')
        load_more = request.GET.get('load_more', 'false') == 'true'

        query = request.GET.get('query', '')
        if query:
            query = unquote(query)

        paginated_products = self.get_page(page)
        current_page = paginated_products.number
        total_pages = self.paginator.num_pages if self.has_items else 0
        has_next = paginated_products.has_next() if self.has_items else False

        pages_to_display = get_pages_to_display(current_page, total_pages) if self.has_items else []

        context = {
            'products': paginated_products,
            'num_pages': total_pages,
            'pages_to_display': pages_to_display,
            'query': query,
            'page_url': request.path,
            'has_items': self.has_items,
            'has_next': has_next,
        }
        if context_extras:
            context.update(context_extras)

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            new_items_html = render_to_string(partial_template, context, request=request)
            new_pagination_html = render_to_string('partials/pagination_catalogue.html', context, request=request)
            return JsonResponse({
                'new_items_html': new_items_html,
                'new_pagination_html': new_pagination_html,
                'current_url': f"{request.path}?{request.GET.urlencode()}",
                'global_min_price': context.get('global_min_price'),
                'global_max_price': context.get('global_max_price'),
                'min_price': context.get('final_min_price'),
                'max_price': context.get('final_max_price'),
            })

        return render(request, template_name, context)


class CataloguePage(View):
    def get(self, request, filters=None):
        product_category_id = request.GET.get('product_category_id')
        product_type_ids = request.GET.getlist('type')
        brand_slug = request.GET.get('brand')
        binding_substance_id = request.GET.get('binding_substance')
        volume_ids = request.GET.getlist('volume')
        is_discounted = True if filters == "discounted-goods" else request.GET.get('is_discounted', 'false') == 'true'
        is_new = True if filters == "new-goods" else request.GET.get('is_new', 'false') == 'true'
        is_in_stock = request.GET.get('is_in_stock', 'false') == 'true'
        sort_type = request.GET.get('sort_type', 'popularity')
        price_gte = request.GET.get('price_gte')
        price_lte = request.GET.get('price_lte')
        # request.user для гостя — AnonymousUser, а не модель с pk; ORM-фильтр
        # по user=request.user на нём падает с TypeError. Берём id напрямую.
        user_id = request.user.pk if request.user.is_authenticated else None
        product_category = None

        if product_category_id:
            try:
                product_category = Category.objects.get(id=product_category_id)
            except (Category.DoesNotExist, ValueError, TypeError):
                product_category = None

        if product_category:
            product_types = ProductType.objects.filter(categories=product_category.id)
        else:
            product_types = ProductType.objects.all()

        products = Product.objects.filter(type__in=product_types).prefetch_related('images').annotate(
            likes_count=Count('favoriteproduct'),
            comments_count=Count('reviews'),
            effective_price=Coalesce(
                Case(
                    When(is_discounted=True, then=F('discount_price')),
                    default=F('price'),
                    output_field=DecimalField()
                ),
                Value(0.0, output_field=DecimalField())
            ),
            is_favorite=Exists(
                FavoriteProduct.objects.filter(
                    user_id=user_id,
                    product=OuterRef('id')
                )
            )
        ).all()

        brand = Brand.objects.filter(slug=brand_slug).first() if brand_slug else None
        if brand:
            products = products.filter(brand=brand)

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

        price_range = products.aggregate(
            min_price=Min('effective_price'),
            max_price=Max('effective_price')
        )
        min_price = int(price_range['min_price']) if price_range['min_price'] is not None else 0
        max_price = int(price_range['max_price']) if price_range['max_price'] is not None else 500

        if price_gte is not None and price_lte is not None:
            try:
                price_gte = float(price_gte)
                price_lte = float(price_lte)
                if price_gte < min_price:
                    price_gte = min_price
                if price_lte > max_price:
                    price_lte = max_price
                products = products.filter(effective_price__gte=price_gte, effective_price__lte=price_lte)
            except (ValueError, TypeError):
                pass

        final_price_range = products.aggregate(
            min_price=Min('effective_price'),
            max_price=Max('effective_price')
        )
        final_min_price = int(final_price_range['min_price']) if final_price_range[
                                                                     'min_price'] is not None else min_price
        final_max_price = int(final_price_range['max_price']) if final_price_range[
                                                                     'max_price'] is not None else max_price

        if sort_type == 'popularity':
            products = products.order_by('-average_rating')
        elif sort_type == 'price':
            products = products.order_by('-effective_price')
        elif sort_type == 'name':
            products = products.order_by('name')

        binding_substances = BindingSubstance.objects.all()
        product_volumes = Volume.objects.all()

        paginator = UniversalPaginator(products, per_page=12)

        # Извлекаем page из request.GET
        page = request.GET.get('page', '1')  # По умолчанию первая страница
        paginated_products = paginator.get_page(page)  # Передаем page в paginator

        context_extras = {
            'product_type': None,
            'page_type': 'catalogue',
            'product_category': product_category,
            'brand': brand,
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
            'min_price': min_price,
            'max_price': max_price,
            'final_min_price': final_min_price,
            'final_max_price': final_max_price,
            'global_min_price': min_price,
            'global_max_price': max_price,
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
        # request.user для гостя — AnonymousUser без pk; фильтр user=request.user
        # на нём падает с TypeError, поэтому берём id напрямую.
        user_id = request.user.pk if request.user.is_authenticated else None
        if query:
            products_list = Product.objects.filter(name__icontains=query).prefetch_related('images').annotate(
                likes_count=Count('favoriteproduct'),
                comments_count=Count('reviews'),
                is_favorite=Exists(
                    FavoriteProduct.objects.filter(
                        user_id=user_id,
                        product=OuterRef('id')
                    )
                )
            ).order_by('name')
        else:
            products_list = Product.objects.prefetch_related('images').annotate(
                likes_count=Count('favoriteproduct'),
                comments_count=Count('reviews'),
                is_favorite=Exists(
                    FavoriteProduct.objects.filter(
                        user_id=user_id,
                        product=OuterRef('id')
                    )
                )
            ).all().order_by('name')

        paginator = UniversalPaginator(products_list, per_page=12)

        return paginator.handle_pagination(
            request,
            template_name='search.html',
            partial_template='partials/products_partial.html',
            context_extras={'query': query, 'page_type': 'search'}
        )

    def post(self, request):
        query = request.POST.get('query', '')
        return redirect(f'/search/?query={query}&page=1' if query else '/search/?page=1')


@method_decorator(login_required, name='dispatch')
class PersonalPage(View):
    def get(self, request):
        orders = Order.objects.filter(user=request.user).prefetch_related(
            'orderproduct_set__product').order_by('-created_at')

        reviews = Review.objects.filter(user=request.user).select_related('product').order_by('-id')
        reviewed_product_ids = reviews.values_list('product_id', flat=True)

        # Предлагаем оставить отзыв только на товары, которые пользователь
        # действительно заказывал и ещё не оценил.
        ordered_product_ids = OrderProduct.objects.filter(
            order__user=request.user
        ).values_list('product_id', flat=True).distinct()
        products_without_review = Product.objects.filter(
            id__in=ordered_product_ids
        ).exclude(id__in=reviewed_product_ids).prefetch_related('images')

        favorite_products_raw = Product.objects.filter(favoriteproduct__user=request.user).prefetch_related(
            'images').annotate(
            likes_count=Count('favoriteproduct'),
            comments_count=Count('reviews'),
            is_favorite=Exists(
                FavoriteProduct.objects.filter(
                    user=request.user,
                    product=OuterRef('id')
                )
            )
        ).all().order_by('name')
        favorite_products = [ProductSelfWrapper(item) for item in favorite_products_raw]
        rated_products_raw = Product.objects.filter(reviews__user=request.user).prefetch_related('images').annotate(
            likes_count=Count('favoriteproduct'),
            comments_count=Count('reviews'),
            is_favorite=Exists(
                FavoriteProduct.objects.filter(
                    user=request.user,
                    product=OuterRef('id')
                )
            ),
            user_rating=F('reviews__rating')
        ).all().order_by('name')
        rated_products = [ProductSelfWrapper(item) for item in rated_products_raw]

        profile = request.user.userprofile
        profile_form = ProfileUpdateForm(user=request.user, initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'company': profile.company,
            'registration_number': profile.registration_number,
            'city': profile.city,
            'postal_code': profile.postal_code,
            'region': profile.region,
        })

        return render(request, 'cabinet.html', {
            'orders': orders,
            'reviews': reviews,
            'products_without_review': products_without_review,
            'favorite_products': favorite_products,
            'rated_products': rated_products,
            'profile_form': profile_form,
            'regions': Region.objects.all(),
        })


class ErrorPage(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'error_page.html', status=404)


class Brands(View):
    def get(self, request):
        return render(request, 'brands.html')


class NewsPage(View):
    def get(self, request):
        category_slug = request.GET.get('category')
        if category_slug:
            news = News.objects.filter(category__slug=category_slug).order_by('-date_published')
        else:
            news = News.objects.all().order_by('-date_published')
        categories = NewsCategory.objects.all()
        return render(request, 'news.html', {
            'news': news,
            'categories': categories,
            'selected_category': category_slug,
        })


class Topic(View):
    def get(self, request, slug):
        news = get_object_or_404(News, slug=slug)

        # Получаем 3 последние новости из той же категории, исключая текущую
        related_news = News.objects.filter(category=news.category).exclude(slug=slug).order_by('-date_published')[:3]

        # Если новостей меньше 3, дополняем последними новостями из других категорий
        if related_news.count() < 3:
            additional_count = 3 - related_news.count()
            additional_news = News.objects.exclude(slug=slug).exclude(category=news.category).order_by(
                '-date_published')[
                              :additional_count]
            related_news = list(related_news) + list(additional_news)
        else:
            related_news = list(related_news)

        return render(request, 'topic.html', {
            'news': news,
            'related_news': related_news
        })


class AboutCompany(View):
    def get(self, request):
        return render(request, 'about_company.html')


class CheckoutPage(View):
    def get(self, request):
        cart = SessionCart(request)
        cart_items = list(cart)
        total_price = cart.get_total_price()
        cities = City.objects.all()

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
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
    template_name = request.GET.get("template", "checkout")
    branches = Branch.objects.filter(city_id=city_id)

    now = datetime.now()
    current_time = now.time()

    DAYS_OF_WEEK_DISPLAY = {
        # винительный падеж: «Забрать в среду»
        'MON': _('понедельник'),
        'TUE': _('вторник'),
        'WED': _('среду'),
        'THU': _('четверг'),
        'FRI': _('пятницу'),
        'SAT': _('субботу'),
        'SUN': _('воскресенье'),
    }

    branches_data = []
    for branch in branches:
        today_schedule = branch.get_today_schedule()
        can_pickup_today = False
        pickup_message = ""
        pickup_hours = ""

        if today_schedule and not today_schedule.is_closed:
            if today_schedule.open_time <= current_time <= today_schedule.close_time:
                can_pickup_today = True
                pickup_message = _("Забрать сегодня")
                pickup_hours = f"{today_schedule.open_time.strftime('%H:%M')} - {today_schedule.close_time.strftime('%H:%M')}"
            else:
                next_day = now
                next_schedule = None
                for i in range(7):
                    next_day += timedelta(days=1)
                    next_weekday = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'][next_day.weekday()]
                    next_schedule = branch.get_schedule(specific_date=next_day.date())
                    if next_schedule and not next_schedule.is_closed:
                        break
                    next_schedule = None

                if next_schedule:
                    day_display = DAYS_OF_WEEK_DISPLAY[next_weekday]
                    if next_day.date() == now.date() + timedelta(days=1):
                        pickup_message = _("Забрать завтра")
                    else:
                        pickup_message = _("Забрать в %(day)s") % {'day': day_display}
                    pickup_hours = f"{next_schedule.open_time.strftime('%H:%M')} - {next_schedule.close_time.strftime('%H:%M')}"
                else:
                    pickup_message = _("Филиал не работает")
                    pickup_hours = ""
        else:
            next_day = now
            next_schedule = None
            for i in range(7):
                next_day += timedelta(days=1)
                next_weekday = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'][next_day.weekday()]
                next_schedule = branch.get_schedule(specific_date=next_day.date())
                if next_schedule and not next_schedule.is_closed:
                    break
                next_schedule = None

            if next_schedule:
                day_display = DAYS_OF_WEEK_DISPLAY[next_weekday]
                if next_day.date() == now.date() + timedelta(days=1):
                    pickup_message = _("Забрать завтра")
                else:
                    pickup_message = _("Забрать в %(day)s") % {'day': day_display}
                pickup_hours = f"{next_schedule.open_time.strftime('%H:%M')} - {next_schedule.close_time.strftime('%H:%M')}"
            else:
                pickup_message = _("Филиал не работает")
                pickup_hours = ""

        branches_data.append({
            'branch': branch,
            'pickup_message': pickup_message,
            'pickup_hours': pickup_hours,
        })

    template_path = "partials/branches_list-checkout.html" if template_name == "checkout" else "partials/branches_list-contacts.html"

    html = render(request, template_path, {
        "branches_data": branches_data,
    }).content.decode("utf-8")
    return JsonResponse({"html": html})


def get_branch_details(request):
    branch_id = request.GET.get("branch_id")
    branch = Branch.objects.get(id=branch_id)

    # Формирование списка телефонных номеров
    phone_numbers = [phone.number for phone in branch.phone_numbers.all()]

    # Формирование списка email
    emails = [email.address for email in branch.email.all()]

    # Формирование расписания с объединением дней с одинаковым временем
    DAY_ORDER = {
        'MON': 1, 'TUE': 2, 'WED': 3, 'THU': 4, 'FRI': 5, 'SAT': 6, 'SUN': 7
    }
    DAYS_SHORT = {
        'MON': _('ПН'), 'TUE': _('ВТ'), 'WED': _('СР'), 'THU': _('ЧТ'), 'FRI': _('ПТ'), 'SAT': _('СБ'), 'SUN': _('ВС')
    }

    # Получаем полное расписание
    schedules = branch.get_schedule()
    schedule_dict = {}
    for schedule in schedules:
        if schedule.is_closed:
            key = "closed"
        else:
            key = f"{schedule.open_time.strftime('%H:%M')}-{schedule.close_time.strftime('%H:%M')}"
        if key not in schedule_dict:
            schedule_dict[key] = []
        schedule_dict[key].append(schedule.day_of_week)

    # Формируем строки расписания
    schedule_lines = []
    for key, days in schedule_dict.items():
        # Сортируем дни по порядку
        days.sort(key=lambda x: DAY_ORDER[x])
        if key == "closed":
            schedule_lines.append(f"{', '.join(DAYS_SHORT[day] for day in days)}: {_('Закрыто')}")
        else:
            # Объединяем последовательные дни в диапазоны
            ranges = []
            start = 0
            for i in range(1, len(days) + 1):
                if i == len(days) or DAY_ORDER[days[i]] != DAY_ORDER[days[i - 1]] + 1:
                    if i - start > 1:
                        ranges.append(f"{DAYS_SHORT[days[start]]}-{DAYS_SHORT[days[i - 1]]}")
                    else:
                        ranges.append(DAYS_SHORT[days[start]])
                    start = i
            schedule_lines.append(f"{', '.join(ranges)}: {key}")

    html = render(request, "partials/branch_details.html", {
        "branch": branch,
        "phone_numbers": phone_numbers,
        "emails": emails,
        "schedule": schedule_lines
    }).content.decode("utf-8")
    return JsonResponse({"html": html})


def apply_promo_code(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip()

        if not code:
            return JsonResponse({"success": False, "error": _("Введите промокод.")}, status=400)

        applied_promo = request.session.get('applied_promo_code')
        if applied_promo == code:
            return JsonResponse({"success": False, "error": _("Этот промокод уже применен.")}, status=400)

        try:
            promo = PromoCode.objects.get(code=code)

            if promo.expiry_date and promo.expiry_date < now():
                return JsonResponse({"success": False, "error": _("Срок действия промокода истек.")}, status=400)

            if promo.max_usage_count is not None and promo.usage_count >= promo.max_usage_count:
                return JsonResponse(
                    {"success": False, "error": _("Этот промокод уже использован максимальное количество раз.")},
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

            return JsonResponse({"success": True, "discount": discount})

        except PromoCode.DoesNotExist:
            return JsonResponse({"success": False, "error": _("Неверный промокод.")}, status=400)

    return JsonResponse({"success": False, "error": _("Неверный метод запроса.")}, status=405)


def create_order(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Проверяем обязательные поля
        required_fields = ['name', 'shipment_method', 'order_place', 'payment_method', 'goods_cost', 'shipment_cost']
        for field in required_fields:
            if field not in data or data[field] is None:
                return JsonResponse({"success": False, "error": _("Поле '%(field)s' обязательно для заполнения.") % {'field': field}},
                                    status=400)

        # Проверяем, что хотя бы одно из полей phone или email заполнено
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        if not phone and not email:
            return JsonResponse({"success": False, "error": _("Необходимо указать хотя бы телефон или email для связи.")},
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
                return JsonResponse({"success": False, "error": _("Не выбрано ни одного товара.")}, status=400)

            # Проверяем промокод
            promo_applied = False
            promo = None
            if promo_code:
                try:
                    promo = PromoCode.objects.get(code=promo_code)
                    promo_applied = True
                except PromoCode.DoesNotExist:
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
                quantity = int(quantity)
                OrderProduct.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity
                )

                # Списываем остаток на складе — только для товаров без вариаций
                # (объём/цвет не заданы) на филиале, откуда оформлен заказ.
                # Для вариативных складов (свой объём/цвет) покупатель пока нигде
                # не выбирает конкретный вариант, поэтому автосписание для них
                # не выполняется — остаток по ним корректируется вручную.
                stock = ProductStock.objects.filter(
                    product=product, branch=order_place,
                    volume__isnull=True, color__isnull=True,
                ).first()
                if stock is not None and stock.quantity is not None:
                    stock.quantity = max(0, stock.quantity - quantity)
                    stock.save(update_fields=['quantity'])

            # Очищаем сессию (если она используется)
            if 'applied_promo_code' in request.session:
                del request.session['applied_promo_code']
            if 'discount' in request.session:
                del request.session['discount']

            # Заказ создан — корзина больше не нужна.
            SessionCart(request).clear()

            return JsonResponse({"success": True, "message": _("Заказ успешно создан!")})

        except Exception:
            # Подробности — только в серверный лог; клиенту незачем видеть
            # внутренний текст исключения (могут утечь детали реализации).
            logger.exception("Ошибка при создании заказа")
            return JsonResponse(
                {"success": False, "error": _("Не удалось оформить заказ. Попробуйте ещё раз.")},
                status=500,
            )

    return JsonResponse({"success": False, "error": _("Неверный метод запроса.")}, status=405)


class TestSlider(View):
    def get(self, request):
        return render(request, 'test_slider.html')


class Test(View):
    def get(self, request):
        categories = Category.objects.filter(mainpagesections__isnull=False)
        print(categories)
        print('\nКатегория 1 id', categories[0].id, '\nКатегория 2 id', categories[1].id, '\n')
        return render(request, 'test.html')


class ShipmentPayment(View):
    def get(self, request):
        cities = City.objects.all()
        return render(request, 'shipment_and_payment.html', {
            'cities': cities,
        })


class Contacts(View):
    def get(self, request):
        cities = City.objects.all()
        return render(request, 'contacts.html', {
            'cities': cities,
        })


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


def _safe_redirect_target(request):
    """HTTP_REFERER — заголовок, который присылает браузер клиента, доверять ему
    напрямую в redirect() нельзя (open redirect). Разрешаем редирект только на
    свой же хост, иначе — на главную."""
    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
            url=referer, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return referer
    return '/'


def _send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    message = render_to_string('acc_active_email.html', {
        'user': user,
        'domain': request.get_host(),
        'uid': uid,
        'token': token,
    })
    send_mail(
        _("Подтверждение регистрации — Mixon Shop"),
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=True,
    )


# ---------------- LOGIN ----------------
def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, _("Вы успешно вошли!"))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return redirect(_safe_redirect_target(request))


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    messages.info(request, _("Вы вышли из аккаунта"))
    return redirect('home')


# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # commit=False: активируем аккаунт только после подтверждения email,
            # поэтому не пользуемся авто-сохранением формы целиком.
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            profile_fields = ['phone', 'company', 'registration_number', 'city', 'postal_code', 'region']
            if hasattr(user, 'userprofile'):
                for field in profile_fields:
                    if field in form.cleaned_data:
                        setattr(user.userprofile, field, form.cleaned_data.get(field))
                user.userprofile.save()

            _send_activation_email(request, user)
            messages.success(
                request,
                _("Регистрация почти завершена — мы отправили письмо со ссылкой "
                  "для подтверждения на указанный email.")
            )
        else:
            # собираем ошибки и передаем через messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    # После обработки всегда редирект на ту же страницу, где есть модалка
    return redirect(_safe_redirect_target(request))


# ---------------- EMAIL ACTIVATE ----------------
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'activation_result.html', {'success': True})

    return render(request, 'activation_result.html', {'success': False})


def _back_to_cabinet_tab(tab):
    return redirect(reverse('cabinet') + f'?tab={tab}')


@login_required
@require_POST
def profile_update(request):
    form = ProfileUpdateForm(request.POST, user=request.user)
    if form.is_valid():
        form.save()
        messages.success(request, _("Данные профиля обновлены."))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    return _back_to_cabinet_tab('contact_information')


@login_required
@require_POST
def change_password_view(request):
    form = PasswordChangeForm(user=request.user, data=request.POST)
    if form.is_valid():
        user = form.save()
        # Иначе смена пароля разлогинит пользователя прямо в его кабинете.
        update_session_auth_hash(request, user)
        messages.success(request, _("Пароль изменён."))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    return _back_to_cabinet_tab('contact_information')


def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    SessionCart(request).add(product, quantity=1)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('cart_detail')


@require_POST
def product_request(request, product_id):
    """Заявка «Быстрый заказ» / «Хочу дешевле» со страницы товара."""
    product = get_object_or_404(Product, id=product_id)
    kind = request.POST.get('kind')
    name = request.POST.get('name', '').strip()
    phone = request.POST.get('phone', '').strip()

    errors = {}
    if kind not in ProductRequest.Kind.values:
        errors['kind'] = _('Неизвестный тип заявки.')
    if not name:
        errors['name'] = _('Укажите имя.')
    if sum(ch.isdigit() for ch in phone) < 10 or len(phone) > 18:
        errors['phone'] = _('Укажите телефон, например +380 67 123 45 67.')
    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    stocks = ProductStock.objects.filter(product=product)
    volume = Volume.objects.filter(id=request.POST.get('volume') or None, productstock__in=stocks).first()
    color = Color.objects.filter(id=request.POST.get('color') or None, productstock__in=stocks).first()

    ProductRequest.objects.create(
        kind=kind, product=product, volume=volume, color=color, name=name[:150], phone=phone,
        comment=request.POST.get('comment', '').strip(),
    )
    return JsonResponse({'success': True})


def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    SessionCart(request).remove(product)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('cart_detail')


@require_POST
def cart_update(request, product_id):
    """Выставляет точное количество товара в корзине (используется страницей
    корзины и счётчиком количества на странице оформления заказа)."""
    product = get_object_or_404(Product, id=product_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        quantity = 1

    cart = SessionCart(request)
    cart.set_quantity(product, quantity)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'quantity': quantity,
            'total_price': float(cart.get_total_price()),
            'total_quantity': cart.get_total_quantity(),
        })
    return redirect('cart_detail')


@require_POST
def cart_clear(request):
    SessionCart(request).clear()
    return redirect('cart_detail')


def cart_detail(request):
    cart = SessionCart(request)
    cart_items = list(cart)

    context = {
        'cart_items': cart_items,
        'total_price': cart.get_total_price(),
        'total_quantity': cart.get_total_quantity(),
    }
    return render(request, 'cart/detail.html', context)


@require_POST
def submit_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    rating = request.POST.get('rating', '0')
    pros = request.POST.get('pros', '')
    cons = request.POST.get('cons', '')
    review_text = request.POST.get('review_text', '')
    reviewer_name = request.POST.get('reviewer_name', '').strip()
    phone = request.POST.get('phone', '').strip()

    try:
        rating_int = int(round(float(rating)))
    except ValueError:
        rating_int = 0

    if not 1 <= rating_int <= 5:
        messages.error(request, _("Пожалуйста, поставьте оценку от 1 до 5 звёзд."))
        return redirect('product', product_id=product.id)

    if request.user.is_authenticated:
        # Повторный отзыв того же пользователя на тот же товар обновляет
        # прежний, а не падает на unique_together('product', 'user').
        Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': rating_int,
                'pros': pros,
                'cons': cons,
                'review_text': review_text,
            },
        )
    else:
        if not reviewer_name:
            messages.error(request, _("Пожалуйста, укажите ваше имя, чтобы оставить отзыв без входа в аккаунт."))
            return redirect('product', product_id=product.id)
        Review.objects.create(
            product=product,
            user=None,
            reviewer_name=reviewer_name,
            phone=phone,
            rating=rating_int,
            pros=pros,
            cons=cons,
            review_text=review_text,
        )

    messages.success(request, _("Спасибо, ваш отзыв опубликован!"))
    return redirect('product', product_id=product.id)


@require_POST
def compare_toggle(request, product_id):
    """Добавить товар в сравнение или убрать (кнопка со «весами» у сердечка)."""
    product = get_object_or_404(Product, id=product_id)
    compare_list = SessionCompare(request)
    status = compare_list.toggle(product)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': status,
            'count': len(compare_list),
            'max': COMPARE_MAX_PRODUCTS,
            'message': _('В сравнение можно добавить не более %(max)d товаров.') % {'max': COMPARE_MAX_PRODUCTS}
            if status == 'full' else '',
        })
    return redirect(_safe_redirect_target(request))


@require_POST
def compare_remove(request, product_id):
    SessionCompare(request).remove(product_id)
    return redirect('compare')


@require_POST
def compare_clear(request):
    SessionCompare(request).clear()
    return redirect('compare')


def compare_page(request):
    """Страница сравнения: товары столбцами, характеристики строками."""
    products = SessionCompare(request).products()
    names = []
    for product in products:
        for item in product.characteristic_values.all():
            if item.value and item.characteristic.name not in names:
                names.append(item.characteristic.name)
    rows = []
    for name in names:
        values = []
        for product in products:
            value = next((i.value for i in product.characteristic_values.all()
                          if i.characteristic.name == name and i.value), '')
            values.append(value)
        rows.append({'name': name, 'values': values, 'differs': len(set(values)) > 1})
    return render(request, 'compare.html', {
        'products': products,
        'rows': rows,
        'max_products': COMPARE_MAX_PRODUCTS,
    })
