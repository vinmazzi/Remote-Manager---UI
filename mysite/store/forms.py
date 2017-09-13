from django import forms

class StoreForm(forms.Form):
    name = forms.CharField(max_length=30)
    code = forms.CharField(max_length=6)
    country = forms.CharField(max_length=40)
    state = forms.CharField(max_length=40)
    city = forms.CharField(max_length=40)
    address = forms.CharField(max_length=40)
