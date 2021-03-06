from django import forms

# Create your models here.

class NetworkForm(forms.Form):
    network_name  = forms.CharField(label="Network Name",max_length=20)
    network_description = forms.CharField(label="Network Description",max_length=100, widget=forms.Textarea())
    network_interface = forms.CharField(label="Network Interface",max_length=6)

class InterfaceForm(forms.Form):
    ip  = forms.CharField(max_length=20, required=False)
    method   = forms.CharField(max_length=20)
    netmask  = forms.CharField(max_length=20, required=False)
    gateway  = forms.CharField(max_length=20, required=False)
