from django import forms

# Create your forms here.

class DnsClientForm(forms.Form):
    domain = forms.CharField(label="Domain Name", max_length=260)
    dns1_address = forms.CharField(label="Dns1 Address", max_length=20)
    dns2_address = forms.CharField(label="Dns2 Address", max_length=20)
