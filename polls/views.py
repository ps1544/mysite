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
Function to retrieve target word list from Solr
"""

def coreSearch(request):
    search_prefill = "Search SEC filings"
    template = loader.get_template('polls/searchresults.html')
    context = {}
    context['search_prefill'] = search_prefill

    # if this is a GET request we need to process the form data
    if request.method == 'POST':
        form = FormNLPSearch()
        context['form'] = form
        
    else:
        # create a form instance and populate it with data from the request:
        form = FormNLPSearch(request.GET)
        
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
    collection = "markets3"

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
    entries = defaultdict(list)

    # The format of JSON search response is different based on whether grouping is enabled or not, handle that here. 
    # TODO: P1: Requires better design so different types of grouping, faceting, filter, or plain flat results can be handled w/o repetitive code
    groupingEnabled = False

    if (groupingEnabled == True):
        url = SOLR_BASE_URL+"/"+collection+"/select?defType=dismax&q="+searchPattern+"&fl=*,score&qf=sentence^10.0+word^1.0+lemma^1.0&rows=100&start=0"
        connection = urllib.request.urlopen(url)
        httpResponse = json.load(connection)
        
        count = httpResponse['response']['numFound']
        if (count > 100):
            count = 100

        i = 0
        
        for each in httpResponse['response']['docs']:
            single_result = []   
            symbol = (each['symbol']).replace("\'", "")
            fileName = each['fileName'].replace("'", "")
            score = each['score']
            single_result.append(symbol)
            single_result.append(fileName)
            if ('word' in each):
                word = each['word'].replace("'", "")
                single_result.append(word)
            elif ('sentence' in each):
                sentence = each['sentence'].replace("'", "")
                single_result.append(sentence)
            single_result.append(score)

            if (i < count):
                entries[i].append(single_result)
                i = i+1
    
    else: 
        """
        The code here requires changes. Code added on 2019-03-28 to support grouping based results to avoid duplicates. 
        1. The word or lemma is not hadled here because such annotations are currently suspended. 
        2. I'm not much excited about how I am parsing the JSON into records. Find a better way if feasible.
        3. Lots of duplicate code with (above) parsing of non-grouped results. 
        """
        grpStatus = "true"
        groupFld = "sentHash"
        url = SOLR_BASE_URL+"/"+collection+"/select?defType=dismax&q="+searchPattern+"&fl=*,score&qf=sentence^10.0+word^1.0+lemma^1.0&group="+grpStatus+"&group%2Efield="+groupFld+"&rows=100&start=0"
        connection = urllib.request.urlopen(url)
        httpResponse = json.load(connection)

        count = 0
        data = httpResponse['grouped']['sentHash']['groups']
        for item in data:
            count += 1
        if (count > 100):
            count = 100

        i = 0
        for each in httpResponse['grouped']['sentHash']['groups']:
            single_result = []   
    
            record = httpResponse['grouped']['sentHash']['groups'][i]['doclist']['docs'][0]
            
            fileName = record['fileName']
            symbol = record['symbol']
            score = record['score']
            sentence = record['sentence']

            single_result.append(symbol)
            single_result.append(fileName)
            single_result.append(score)
            single_result.append(sentence)
            
            if (i < count):
                entries[i].append(single_result)
                i = i+1
        

    #pprint(entries)
    # See: https://stackoverflow.com/questions/32813500/items-not-working-on-defaultdict-in-django-template
    dictEntries = dict(entries)
    return dictEntries




if __name__ == "__main__":
    symbol = "aapl"
    request = "request"
    fileName = ""
    count = 1
    words = "pfizer merck sanofi"
    request = ""
    coreSearch(request)
    
    #dailyReturnsForAll(request)
