from django import forms

class FormFilingSearch(forms.Form):
    searchFilings_form = forms.CharField(
    initial='Company Symbol / Name', 
    max_length=100, 
    #help_text='A valid email address, please.',
    required=False)
