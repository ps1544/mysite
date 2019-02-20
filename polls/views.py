import pandas as pd 
import numpy as np 
import tensorflow as tf 
import sqlalchemy 
import sklearn 
import time
import os
import pprint
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
from os.path import isdir
from os.path import abspath


def connectSQL():
    username = "psharma"
    pwd = "$ys8dmin"
    engine = create_engine(('mysql+mysqlconnector://'+username+':'+pwd+'@localhost/markets'))
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

    qLatestDate = "select distinct date from " +tblNameCurrent+ " order by date desc limit 0,1"
    dfDate = executeQuery(connection, qLatestDate)
    latestDate = dfDate.iloc[0, 0]
    strDate = latestDate.strftime("%Y-%m-%d")
    #print("The latest date is:", strDate)

    #query = "select *, close * volume as 'DlrVolume' from " +tblNameCurrent+ " where date like '" +strDate+ "' order by DlrVolume desc"
    #dfrm = executeQuery(connection, query)

    order_by = request.GET.get('order_by', 'DlrVolume')
    #order_by = request.GET.get('order_by')
    if (type(order_by) == str):
        query = "select *, close * volume as 'DlrVolume' from " +tblNameCurrent+ " where date like '" +strDate+ "' order by " +order_by+ " desc"
        dfrmFull = executeQuery(connection, query)
        dfrm = dfrmFull[['name', 'symbol', 'open', 'high', 'low', 'close', 'netChange', 'pcntChange', 'volume', 'peRatio', 'ytdPcntChange', 'exchange', 'DlrVolume']]        
        paginator = Paginator(dfrm.values.tolist(), 100) # Show 25 contacts per page
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
        query = "SELECT *, close * volume as 'DlrVolume' from " +tblNameCurrent+ " where symbol like '" +symbol+ "' order by " +order_by+ " desc"
        dfrmFull = executeQuery(connection, query)
        dfrm = dfrmFull[['name', 'symbol', 'open', 'high', 'low', 'close', 'netChange', 'pcntChange', 'volume', 'high52Weeks', 'low52Weeks', 'dividend', 'yield', 'peRatio', 'ytdPcntChange', 'exchange', 'date', 'DlrVolume']]
        paginator = Paginator(dfrm.values.tolist(), 50) # Show N contacts per page
        page = request.GET.get('page')
        pagedList = paginator.get_page(page)
    

    
    if (dfrm.size == 0):
        raise Http404("Symbol %s not found in catalog." % symbol)
    else:
        #return render(request, 'polls/returnsBySymbol.html', {'contacts': listDlyReturns})
        
        template = loader.get_template('polls/dailyReturnsBySymbol.html')
        context = {
            #'dfrm_list': dfrm.values.tolist(),
            'pagedList': pagedList,
            'symbol': symbol.upper(),
        }
        return HttpResponse(template.render(context, request))
        

"""
Function to traverse file structure from a certain path
"""
def retrieveDirsMatchingNames(baseDir, listNames):
    retDirListing = []
    pp = pprint.PrettyPrinter(indent=4)
    contents = os.listdir(baseDir)
    
    for content in contents:
        if content in listNames:
            path = os.path.join(baseDir, content)
            if os.path.isdir(path):
                retDirListing.append(path)

    return retDirListing


def filingsTypesBySymbol(request, symbol):
    pp = pprint.PrettyPrinter(indent=4)    
    connection = connectSQL()
    tblNameCurrent = "equities_2018"
    filings = ["10-K", "424B2", "FWP", "10-Q"]

    # First, retrieve list of symbols
    qLatestDate = "select distinct symbol from " +tblNameCurrent+ ""
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

def viewFilingWoExt(request, symbol, filingType, fileName):
    baseDir = "C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols"
    #fileName = fileName + ".htm"
    path = os.path.join(baseDir, symbol, filingType, fileName)
    print(path)

    if os.path.exists(path) and os.path.isfile(path):
        f = open(path, 'r')
        file_contents = f.read()
        f.close()
        
    template = loader.get_template('polls/filingsAndSearch.html')
    context = {
        'filings': file_contents,
    }
    return HttpResponse(template.render(context, request))
            #else:
            #return HttpResponse(file_content, content_type="text/html")
    #else:
     #   return HttpResponse("File not found.") #TODO: Improve error as well as the message

    

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


def viewFilingPath(request, path):
    baseDir = "C:/Users/pshar/Dropbox/Programming/SampleTexts/FilingsBySymbols"
    contents = path.split("/")
    symbol = contents[1]
    filingType = contents[2]
    fileName = contents[3]
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(symbol)
    pp.pprint(filingType)
    pp.pprint(fileName)

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


def jstest(request):
    filings = ["a", "b"]
    template = loader.get_template('polls/jstest.html')
    context = {
        'filings': filings,
    }
    return HttpResponse(template.render(context, request))


if __name__ == "__main__":
    symbol = "gs"
    request = "request"
    dailyReturnsForAll(request)

