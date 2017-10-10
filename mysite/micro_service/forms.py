from django import forms

class RegistryForm(forms.Form):
    name = forms.CharField(label="Name", max_length=20)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())
    url = forms.CharField(label="URL", max_length=100)
    port = forms.CharField(label="Port", max_length=5)
    user = forms.CharField(label="Username", max_length=20, required=False)
    password = forms.CharField(label="Password", max_length=50, required=False, widget=forms.PasswordInput())
    email = forms.CharField(label="Email", max_length=40, required=False)
    ca_crt = forms.CharField(label="CA Certificate", max_length=5000, required=False, widget=forms.Textarea())

class ImageForm(forms.Form):
    name = forms.CharField(label="Name", max_length=20)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())

class ContainerCatalogForm(forms.Form):
    name = forms.CharField(label="Name", max_length=20)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())
    image_name  = forms.CharField(label="Image Name", max_length=100)
    host_octect  = forms.CharField(label="Host Ip octect", max_length=3)
