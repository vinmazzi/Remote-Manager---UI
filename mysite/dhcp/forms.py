from django import forms

class DhcpServiceForm(forms.Form):
    nameservers = forms.CharField(max_length=150)
    ntpservers = forms.CharField(max_length=150)
    interfaces = forms.CharField(max_length=150)
    pxeserver  = forms.CharField(max_length=150)
    pxefilename  = forms.CharField(max_length=150)
    dnsdomain  = forms.CharField(max_length=150)

class DhcpPoolForm(forms.Form):
    domain = forms.CharField(max_length=150)
    network = forms.CharField(max_length=150)
    mask    = forms.CharField(label="Netmask", max_length=150)
    gateway = forms.CharField(label="Gateway", max_length=150)
    network_range = forms.CharField(label="Network Range", max_length=150)
