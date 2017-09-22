from django.db import forms

# Create your models here.

class UserForm(forms.Form):
    username = forms.CharField(max_length=20)
    email = forms.CharField(max_length=20)
    name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)
