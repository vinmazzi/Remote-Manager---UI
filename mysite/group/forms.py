from django import forms

class GroupForm(forms.Form):
    group_name_text  = forms.CharField(label='Group Name' ,max_length=300)
    group_alias_text = forms.CharField(label='Group Alias' ,max_length=300)
    group_description = forms.CharField(label='Group Description' ,max_length=300, widget=forms.Textarea())
