from django import forms

class FwRuleForm(forms.Form):
    rule_name_text = forms.CharField(label='Rule Name' ,max_length=150)
    source         = forms.CharField(label='Source Ip' ,max_length=20, required=False)
    destination    = forms.CharField(label='Destination Ip' ,max_length=20, required=False)
    proto          = forms.CharField(label='Protocol' ,max_length=7, required=False)
    chain          = forms.CharField(label='Chain' ,max_length=15, required=False)
    action         = forms.CharField(label='Action' ,max_length=11, required=False)
    table          = forms.CharField(label='Table' ,max_length=10, required=False)
    sport          = forms.IntegerField(label='Source Port', required=False)
    dport          = forms.IntegerField(label='Destination Port', required=False)

