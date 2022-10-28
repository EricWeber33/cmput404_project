from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import CharField

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(label='Password', widget=forms.PasswordInput())

class RegisterForm(UserCreationForm):
    displayName = forms.CharField(label='Display Name')
    github = forms.CharField(label='Github URL')
    profileImage = CharField(label='Profile Image URL')
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'displayName', 'github', 'profileImage']
