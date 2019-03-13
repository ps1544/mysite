from django import forms

class NameForm(forms.Form):
    search_form = forms.CharField(label='Search:', max_length=100)
    