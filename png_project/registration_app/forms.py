from .models import *
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django import forms
from django.contrib.auth.models import User


# Form for company registration
class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'email', 'logo', 'banner','banner_content', 'description','services', 'password','website_url','youtube_url', 'instagram_url', 'facebook_url','linkedin_url','title']


# Form for login, where email is used as the username
class LoginForm(AuthenticationForm):
    username = forms.EmailField(max_length=254, widget=forms.TextInput(attrs={'autofocus': True}))  # Use email for login
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Enter your registered email", max_length=254)
    new_password = forms.CharField(label="New Password", widget=forms.PasswordInput)


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = '__all__'  # Include all fields, including password
        exclude = ['bullet_points']


class NewsForm(forms.ModelForm):
    class Meta:
        model = NewsUpload
        fields = ['news_img', 'title', 'content', 'author']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['event_img', 'name', 'location', 'description']