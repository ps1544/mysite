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
from tensorflow.contrib.layers import fully_connected

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render
from django.template import loader
from django.http import HttpResponseRedirect
from django.shortcuts import render

from os.path import isdir
from os.path import abspath
from urllib import *
from collections import defaultdict

from .FormNLPSearch import FormNLPSearch
from .FormFilingSearch import FormFilingSearch



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


"""
- Should have a symbol search page
- 
"""
def filingsBasePage(request):
    
    connection = connectSQL()
    tblNameCurrent = "equities_2018"

    search_prefill = "Company Name/Symbol"
    template = loader.get_template('polls/filingsBasePage.html')
    context = {}
    context['search_prefill'] = search_prefill

    # if this is a GET request we need to process the form data
    if request.method == 'POST':
        form = FormFilingSearch()
        context['form'] = form
    else:
        # create a form instance and populate it with data from the request:
        form = FormFilingSearch(request.GET)
        
        # check whether it's valid:
        if form.is_valid():
            symbol = form.cleaned_data['searchFilings_form']
            print("Filings for: "+symbol)
            context['form'] = form
            
    # TODO: Template is not defined in certain cases. Handle all scenarios
    return HttpResponse(template.render(context, request))


"""
Function to traverse file structure from a certain path
"""

def retrieveDirsMatchingNames(baseDir, listNames):
    retDirListing = []
    
    contents = os.listdir(baseDir)

    for content in contents:
        if content in listNames:
            path = os.path.join(baseDir, content)
            if os.path.isdir(path):
                retDirListing.append(path)

    return retDirListing


def filingsTypesBySymbol(request, symbol):
    connection = connectSQL()
    tblNameCurrent = "equities_2018"
    filings = ["10-K", "424B2", "FWP", "10-Q"]

    # First, retrieve list of symbols
    qLatestDate = "select distinct symbol from " + tblNameCurrent + ""
    dfSymbols = executeQuery(connection, qLatestDate)
    symbols = dfSymbols.iloc[:, 0]

    # Now, get the path where all files are present
    baseDir = "C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols"
    dirsSymbols = retrieveDirsMatchingNames(baseDir, symbols.tolist())
    symbols = []
    for dirSymbol in dirsSymbols:
        (head, tail) = os.path.split(dirSymbol)
        symbols.append(tail)

    dirsFilings = []

    if symbol in symbols:
        path = os.path.join(baseDir, symbol)
        dirsFilingTypes = os.listdir(path)
        for dirFilingTypes in dirsFilingTypes:
            dirsFilings.append(symbol+"/"+dirFilingTypes)

        template = loader.get_template('polls/filingsTypesBySymbol.html')
        context = {
            'dirsFilings': dirsFilings,
            'search_prefill' : "Search SEC filings",
        }
        return HttpResponse(template.render(context, request))
    else:
        return HttpResponse("Data NOT found for symbol", symbol)

    connection.close()


def filingsByGivenTypeForSymbol(request, symbol, filingType):
    baseDir = "C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols"
    pathSymbol = os.path.join(baseDir, symbol)
    pathSymbolFilings = os.path.join(pathSymbol, filingType)

    filings = []
    contents = os.listdir(pathSymbolFilings)

    for content in contents:
        #content = os.path.splitext(content)[0]
        filings.append(symbol+"/"+filingType+"/"+content)

    template = loader.get_template('polls/filingsByGivenTypeForSymbol.html')
    context = {
        'filings': filings,
    }
    return HttpResponse(template.render(context, request))


"""
Handles URLs that had any regex (file ext, hyphens) removed. Removal of
regex patterns is essentially a hack until I can make regex url work in 
Django. Posted on Stack Overflow as well but to no avail. 
"""
def viewFilingWoExt(request, symbol, filingType, fileName):
    baseDir = "C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols"
    #fileName = fileName + ".htm"
    path = os.path.join(baseDir, symbol, filingType, fileName)
    print(path)

    if os.path.exists(path) and os.path.isfile(path):
        f = open(path, 'r')
        file_contents = f.read()
        f.close()

    #word_list = ["red", "orange", "green"]
    symbol = "aapl"
    fileName = "a10qq32017712017htm.txt"
    count = "40" # TODO: Handle this properly as int
    word_list = querySolrForKeywords(symbol, fileName, count)
    search_prefill = "Company Name/Ticker"
    
    template = loader.get_template('polls/filingsAndSearch.html')
    context = {
        'contents': file_contents,
        'word_list' : word_list,
        'symbol' : symbol,
        'search_prefill' : "Search SEC filings",
    }
    return HttpResponse(template.render(context, request))
    
"""
Added for regex based URL. Didn't work but keep it in case
a fix is later found. 
"""
def viewFiling(request, symbol, filingType, fileName, fileExt):
    baseDir = "C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols"
    path = os.path.join(baseDir, symbol, filingType, fileName, ".", fileExt)
    if os.path.exists(path) and os.path.isfile(path):
        f = open(path, 'r')
        file_content = f.read()
        f.close()
        if file_content == "":
            return HttpResponse("File contents empty.")
        else:
            return HttpResponse(file_content, content_type="text/html")
    else:
        return HttpResponse("File not found.")


"""
Added for regex based URL. Didn't work but keep it in case
a fix is later found. "Path" can be used for the full URL here. 
"""
def viewFilingPath(request, path):
    baseDir = "C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols"
    contents = path.split("/")
    symbol = contents[1]
    filingType = contents[2]
    fileName = contents[3]
    
    """
    pp.pprint(symbol)
    pp.pprint(filingType)
    pp.pprint(fileName)
    """
    lclPath = os.path.join(baseDir, symbol, filingType, fileName)
    if os.path.exists(lclPath) and os.path.isfile(lclPath):
        f = open(lclPath, 'r')
        file_content = f.read()
        f.close()
        if file_content == "":
            return HttpResponse("File contents empty.")
        else:
            return HttpResponse(file_content, content_type="text/plain")
    else:
        return HttpResponse("File not found.")

def querySolrForKeywords(symbol, fileName, count):
    words = []
    SOLR_BASE_URL = "http://localhost:8984/solr"
    collection = "markets"
    url = SOLR_BASE_URL+"/"+collection+"/select?defType=lucene&q=*:*&fl=word+pos+symbol+fileName&fq=fileName:\""+fileName+"\"&fq=symbol:"+symbol+"&fq=pos:NNP&rows="+count+"&start=0"
    connection = urllib.request.urlopen(url)
    httpResponse = json.load(connection)
    #pprint(httpResponse)
    for each in httpResponse['response']['docs']:
        word = each['word']
        #pprint(each['word'])
        words.append(word)
    #pprint(words)
    return words

