from django import forms

# Create your forms here.

class VpcForm(forms.Form):
    name = forms.CharField(label="Name", max_length=90)
    cidr_block = forms.CharField(label="Network", max_length=20)
#    region = forms.CharField(label="Region", max_length=35)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())

class SubnetForm(forms.Form):
    name = forms.CharField(label="Name", max_length=90)
    cidr_block = forms.CharField(label="Subnet", max_length=20)
#    region = forms.CharField(label="Region", max_length=35, required=False, widget=forms.Textarea())
    description = forms.CharField(max_length=100)

class SecurityGroupForm(forms.Form):
    name = forms.CharField(label="Name", max_length=20)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())


class SecurityGroup_RuleForm(forms.Form):
    name = forms.CharField(label="Rule Name", max_length=90)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())
    protocol = forms.CharField(label="Protocol", max_length=100)
    port = forms.CharField(label="Source Port", max_length=8)
    cidr = forms.CharField(label="Source", max_length=20)

class CloudConfigurationGroupForm(forms.Form):
    name = forms.CharField(label="Name", max_length=90)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())

class CloudInstanceForm(forms.Form):
    name = forms.CharField(label="Name", max_length=90)
    description = forms.CharField(label="Description", max_length=100, widget=forms.Textarea())
