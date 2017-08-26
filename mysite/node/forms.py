from django import forms

class NodeForm(forms.Form):
    name = forms.CharField(max_length=20)
    serial_number = forms.CharField(max_length=22)
    lan1_method = forms.CharField(max_length=8)
    lan1_ip = forms.CharField(max_length=20, required=False)
    lan1_netmask = forms.CharField(max_length=20, required=False)
    lan1_gateway = forms.CharField(max_length=20, required=False)
    dns1_ip = forms.CharField(max_length=20)
    dns2_ip = forms.CharField(max_length=20, required=False)
    dns_domain = forms.CharField(max_length=30, required=False)
    dns_search = forms.CharField(max_length=30, required=False)
