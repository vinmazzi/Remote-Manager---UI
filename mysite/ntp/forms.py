from django import forms

class NtpForm(forms.Form):
    servers  = forms.CharField(max_length=46)
