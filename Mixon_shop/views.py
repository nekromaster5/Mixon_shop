from django.shortcuts import redirect, render
from django.urls import reverse_lazy as _
from django.views import View
# Existing import statements
from django.shortcuts import render, get_object_or_404
from .models import Product
from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth import views as auth_views
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Делаем пользователя неактивным до подтверждения почты
            user.save()

            # Создаем профиль пользователя
            UserProfile.objects.create(
                user=user,
                phone=form.cleaned_data.get('phone', ''),
                city=form.cleaned_data.get('city', ''),
                postal_code=form.cleaned_data.get('postal_code', ''),
                region=form.cleaned_data.get('region', None)
            )

            # Отправка письма с подтверждением
            current_site = get_current_site(request)
            mail_subject = 'Activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()

            return JsonResponse({'success': True, 'message': 'Please confirm your email address to complete the registration'})
        else:
            errors = form.errors.as_json()
            return JsonResponse({'success': False, 'message': 'Form is invalid. Please check the entered data.', 'errors': errors})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Your account has been confirmed.')
        return redirect('login')
    else:
        messages.warning(request, 'Activation link is invalid!')
        return redirect('home')
class HomePage(View):
    def get(self, request):
        return render(request, 'home_page.html')


class CataloguePage(View):
    def get(self, request):
        return render(request, 'catalogue.html')

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