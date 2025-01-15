from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User  # Импортируем кастомную модель пользователя

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User  # Используем кастомную модель пользователя
        fields = ['username', 'email', 'password1', 'password2']