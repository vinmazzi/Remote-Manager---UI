from django import forms

class DhcpServiceForm(forms.Form):
    nameservers = forms.CharField(max_length=150)
    ntpservers = forms.CharField(max_length=150)
    interfaces = forms.CharField(max_length=150)
    pxeserver  = forms.CharField(max_length=150)
    pxefilename  = forms.CharField(max_length=150)
    dnsdomain  = forms.CharField(max_length=150)

class DhcpPoolForm(forms.Form):
    mask    = forms.CharField(max_length=150)
    gateway = forms.CharField(max_length=150)
    network_range = forms.CharField(max_length=150)
