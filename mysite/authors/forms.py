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
    profileImage = forms.CharField(label='Profile Image URL', initial = 'https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_960_720.png')
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'email', 'displayName', 'github', 'profileImage']

class RemoteRegisterForm(forms.Form):
    remote_author = forms.URLField(label="Remote Author")
    username = forms.CharField(label="Remote User")
    password = forms.CharField(label="Remote Password", widget=forms.PasswordInput())

