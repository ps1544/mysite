import datetime
import pandas as pd
import numpy as np
import tensorflow as tf
import sqlalchemy
import sklearn
import time
import os
import pprint
import json
import urllib.request
from pprint import pprint
from datetime import datetime
from sqlalchemy import create_engine
from scipy import stats
from numpy import newaxis
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

def connectSQL():
    username = "psharma"
    pwd = "$ys8dmin"
    engine = create_engine(
        ('mysql+mysqlconnector://'+username+':'+pwd+'@localhost/markets'))
    connection = engine.connect()
    return connection


def executeQuery(connection, query):
    dfrm = pd.read_sql(query, connection)
    #print (dfrm)
    return dfrm

def retrieveSymbolsList():
    connection = connectSQL()
    tblNameCurrent = "equities_2018"
    symbols = []

    # First, retrieve list of symbols
    query = "select distinct symbol from " + tblNameCurrent + ""
    dfSymbols = executeQuery(connection, query)
    symbols = dfSymbols.iloc[:, 0]

    return symbols

class FormFilingSearch(forms.Form):
    searchFilings_form = forms.CharField(
    initial='Company Symbol / Name', 
    max_length=100, 
    #help_text='A valid email address, please.',
    required=True)
    

    def clean_searchFilings_form(self):
        formData = self.cleaned_data['searchFilings_form']
        symbols = retrieveSymbolsList()
        
        # Check if symbol is valid:
        if formData.upper() not in symbols.tolist():
            raise ValidationError(_('Symbol '+formData+' not found in catalog. Retry!'))
        
        # Remember to always return the cleaned data.
        return formData




