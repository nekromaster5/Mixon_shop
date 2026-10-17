from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import UserProfile, Region


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=18, required=False)
    company = forms.CharField(max_length=256, required=False)
    registration_number = forms.CharField(max_length=256, required=False)
    city = forms.CharField(max_length=256, required=True)
    postal_code = forms.CharField(max_length=10, required=False)
    region = forms.ModelChoiceField(queryset=Region.objects.all(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2',
                  'phone', 'company', 'registration_number', 'city', 'postal_code', 'region']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            user_profile = user.userprofile
            user_profile.phone = self.cleaned_data.get('phone')
            user_profile.company = self.cleaned_data.get('company')
            user_profile.registration_number = self.cleaned_data.get('registration_number')
            user_profile.city = self.cleaned_data.get('city')
            user_profile.postal_code = self.cleaned_data.get('postal_code')
            user_profile.region = self.cleaned_data.get('region')
            user_profile.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label="Имя пользователя")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class ProfileUpdateForm(forms.Form):
    """Вкладка «Контактная информация» в личном кабинете — те же поля, что
    заполняются при регистрации, только для редактирования уже существующего
    аккаунта."""
    first_name = forms.CharField(max_length=150, required=False, label='Имя')
    last_name = forms.CharField(max_length=150, required=False, label='Фамилия')
    email = forms.EmailField(required=True, label='E-mail')
    phone = forms.CharField(max_length=18, required=False, label='Телефон')
    company = forms.CharField(max_length=256, required=False, label='Компания')
    registration_number = forms.CharField(max_length=256, required=False, label='Регистрационный номер')
    city = forms.CharField(max_length=256, required=True, label='Город')
    postal_code = forms.CharField(max_length=10, required=False, label='Почтовый индекс')
    region = forms.ModelChoiceField(queryset=Region.objects.all(), required=False, label='Область')

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise forms.ValidationError("Этот email уже используется другим аккаунтом.")
        return email

    def save(self):
        user = self.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()

        profile = user.userprofile
        profile.phone = self.cleaned_data['phone']
        profile.company = self.cleaned_data['company']
        profile.registration_number = self.cleaned_data['registration_number']
        profile.city = self.cleaned_data['city']
        profile.postal_code = self.cleaned_data['postal_code']
        profile.region = self.cleaned_data['region']
        profile.save()
        return user
