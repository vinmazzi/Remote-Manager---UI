from django import forms

class NodeForm(forms.Form):
    name = forms.CharField(max_length=20)
    serial_number = forms.CharField(max_length=22)
    dns1_ip = forms.CharField(max_length=20)
    dns2_ip = forms.CharField(max_length=20, required=False)
    dns_domain = forms.CharField(max_length=30, required=False)
    dns_search = forms.CharField(max_length=30, required=False)
