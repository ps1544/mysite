from django import forms

class FormNLPSearch(forms.Form):
    search_form = forms.CharField(
        initial='Search SEC filings', 
        max_length=100, 
    #   help_text='A valid email address, please.',
        required=False)