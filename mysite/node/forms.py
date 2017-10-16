from django import forms

class NodeForm(forms.Form):
    name = forms.CharField(max_length=20)
    serial_number = forms.CharField(max_length=22)
    store = forms.CharField(max_length=200, required=False)
