from django import forms

class ClientForm(forms.Form):
    client_name_text  = forms.CharField(label='Client Name' ,max_length=300)
