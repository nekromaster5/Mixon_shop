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
