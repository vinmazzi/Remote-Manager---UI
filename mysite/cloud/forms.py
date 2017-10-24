from django import forms

# Create your forms here.

class Vpc(forms.Form):
    name = forms.CharField(label="Name", max_length=20)
    cidr_block = forms.CharField(label="Network", max_length=20)
    region = forms.CharField(label="Region", max_length=35)

class Subnet(forms.Form):
    name = forms.CharField(label="Name", max_length=20)
    cidr_block = forms.CharField(label="Network", max_length=20)
    region = forms.CharField(label="Region", max_length=35)
