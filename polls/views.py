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

from .forms import NameForm


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


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)


def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)


def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)


def dailyReturnsForAll(request):
    connection = connectSQL()
    tblNameCurrent = "equities_2018"

    qLatestDate = "select distinct date from " + \
        tblNameCurrent + " order by date desc limit 0,1"
    dfDate = executeQuery(connection, qLatestDate)
    latestDate = dfDate.iloc[0, 0]
    strDate = latestDate.strftime("%Y-%m-%d")
    #print("The latest date is:", strDate)

    #query = "select *, close * volume as 'DlrVolume' from " +tblNameCurrent+ " where date like '" +strDate+ "' order by DlrVolume desc"
    #dfrm = executeQuery(connection, query)

    order_by = request.GET.get('order_by', 'DlrVolume')
    #order_by = request.GET.get('order_by')
    if (type(order_by) == str):
        query = "select *, close * volume as 'DlrVolume' from " + tblNameCurrent + \
            " where date like '" + strDate + "' order by " + order_by + " desc"
        dfrmFull = executeQuery(connection, query)
        dfrm = dfrmFull[['name', 'symbol', 'open', 'high', 'low', 'close', 'netChange',
                         'pcntChange', 'volume', 'peRatio', 'ytdPcntChange', 'exchange', 'DlrVolume']]
        # Show 25 contacts per page
        paginator = Paginator(dfrm.values.tolist(), 100)
        page = request.GET.get('page')
        pagedList = paginator.get_page(page)

    seriesSymbols = dfrm.loc[:, "symbol"]
    listSymbols = seriesSymbols.tolist()

    if (dfrm.size == 0):
        raise Http404("Problems with retrieving dataset from catalog.")
    else:
        template = loader.get_template('polls/dailyReturnsForAll.html')
        context = {
            'pagedList': pagedList,
            'dfrm_symbols': listSymbols,
            'search_prefill' : "Search SEC filings",
        }
        return HttpResponse(template.render(context, request))

    # TODO: How to close the SQL connection here w/o affecting later clicks?
    # connection.close()


"""
Function to print returns of a single symbol
"""


def dailyReturnsBySymbol(request, symbol):
    connection = connectSQL()
    tblNameCurrent = "equities_2018"

    #query = "SELECT *, close * volume as 'DlrVolume' from " +tblNameCurrent+ " where symbol like '" +symbol+ "' order by date desc limit 0, 300;"
    #dfrm = executeQuery(connection, query)
    #listDlyReturns = dfrm.values.tolist(),

    order_by = request.GET.get('order_by', 'date')
    #order_by = request.GET.get('order_by')

    if (type(order_by) == str):
        #query = "select *, close * volume as 'DlrVolume' from " +tblNameCurrent+ " where date like '" +strDate+ "' order by " +order_by+ " desc"
        query = "SELECT *, close * volume as 'DlrVolume' from " + tblNameCurrent + \
            " where symbol like '" + symbol + "' order by " + order_by + " desc"
        dfrmFull = executeQuery(connection, query)
        dfrm = dfrmFull[['name', 'symbol', 'open', 'high', 'low', 'close', 'netChange', 'pcntChange', 'volume',
                         'high52Weeks', 'low52Weeks', 'dividend', 'yield', 'peRatio', 'ytdPcntChange', 'exchange', 'date', 'DlrVolume']]
        # Show N contacts per page
        paginator = Paginator(dfrm.values.tolist(), 50)
        page = request.GET.get('page')
        pagedList = paginator.get_page(page)

    if (dfrm.size == 0):
        raise Http404("Symbol %s not found in catalog." % symbol)
    else:
        # return render(request, 'polls/returnsBySymbol.html', {'contacts': listDlyReturns})

        template = loader.get_template('polls/dailyReturnsBySymbol.html')
        context = {
            # 'dfrm_list': dfrm.values.tolist(),
            'pagedList': pagedList,
            'symbol': symbol.upper(),
            'search_prefill' : "Search SEC filings",
        }
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


"""
Function to retrieve target word list from Solr
"""

def coreSearch(request):
    search_prefill = "Search SEC filings"
    template = loader.get_template('polls/searchresults.html')
    context = {}
    context['search_prefill'] = search_prefill

    # if this is a GET request we need to process the form data
    if request.method == 'POST':
        form = NameForm()
        context['form'] = form
        
    else:
        # create a form instance and populate it with data from the request:
        form = NameForm(request.GET)
        
        # check whether it's valid:
        if form.is_valid():
            words = form.cleaned_data['search_form']
            print(words) 
            results = queryForCoreSearch(words)
            context['results'] = results
            context['form'] = form
            
    # TODO: Handle POST in some default manner as well

    # TODO: Template is not defined in certain cases. Handle all scenarios
    return HttpResponse(template.render(context, request))

def queryForCoreSearch(listWords):
    
    SOLR_BASE_URL = "http://localhost:8984/solr"
    collection = "markets"

    """
    words = ""
    if (listWords == ""):
        listWords = ["liability", "credit", "risk"]
    words = listWords.split()
    for word in words:
        words += ('%2B')+word
    """
    searchPattern = ""
    words = listWords.split()
    for word in words:
        searchPattern += ('%2B')+word
    print(searchPattern) 
    
    url = SOLR_BASE_URL+"/"+collection+"/select?defType=dismax&q="+searchPattern+"&fl=*,score&qf=sentence^10.0+word^1.0+lemma^1.0&rows=100&start=0"
    connection = urllib.request.urlopen(url)
    httpResponse = json.load(connection)
    
    count = httpResponse['response']['numFound']
    if (count > 100):
        count = 100

    entries = defaultdict(list)
    i = 0
    
    for each in httpResponse['response']['docs']:
        single_result = []   
        symbol = (each['symbol'][0]).replace("\'", "")
        fileName = each['fileName'][0].replace("'", "")
        score = each['score']
        single_result.append(symbol)
        single_result.append(fileName)
        if ('word' in each):
            word = each['word'][0].replace("'", "")
            single_result.append(word)
        elif ('sentence' in each):
            sentence = each['sentence'][0].replace("'", "")
            single_result.append(sentence)
        single_result.append(score)

        if (i < count):
            entries[i].append(single_result)
            i = i+1

    #pprint(entries)
    # See: https://stackoverflow.com/questions/32813500/items-not-working-on-defaultdict-in-django-template
    dictEntries = dict(entries)
    return dictEntries



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


if __name__ == "__main__":
    symbol = "aapl"
    request = "request"
    fileName = ""
    count = 1
    words = "pfizer merck sanofi"
    request = ""
    coreSearch(request)
    
    #dailyReturnsForAll(request)
