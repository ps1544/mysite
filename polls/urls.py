from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from . import views
from . import viewsFilings

urlpatterns = [
    # ex: /polls/
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:question_id>/', views.detail, name='detail'),
    # ex: /polls/5/results/
    path('<int:question_id>/results/', views.results, name='results'),
    # ex: /polls/5/vote/
    path('<int:question_id>/vote/', views.vote, name='vote'),
    
    # ex: /polls/dailyReturns/
    path('dailyReturns/', views.dailyReturnsForAll, name='dailyReturnsForAll'),

    # ex: /polls/search/
    path('search/', views.coreSearch, name='coreSearch'),
    
    # ex: /polls/dailyReturns/<SYMBOL>
    path('dailyReturnsBySymbol/<slug:symbol>/', views.dailyReturnsBySymbol, name='dailyReturnsBySymbol'),
    
    # ex: /polls/filings/
    path('filings/', viewsFilings.filingsBasePage, name='filingsBasePage'),
    
    # ex: /polls/filings/<SYMBOL>
    path('filings/<slug:symbol>/', viewsFilings.filingsTypesBySymbol, name='filingsTypesBySymbol'),
    # ex: /polls/filings/<SYMBOL>/<Filing_Type>
    path('filings/<slug:symbol>/<slug:filingType>/', viewsFilings.filingsByGivenTypeForSymbol, name='filingsByGivenTypeForSymbol'),
    # ex: /polls/filings/<SYMBOL>/<Filing_Type>/<fileName.htm>
    path('filings/<slug:symbol>/<slug:filingType>/<slug:fileName>', viewsFilings.viewFilingWoExt, name='viewFilingWoExt'),


    #path('path', viewsFilings.viewFilingPath, name='viewFilingPath'),

    re_path(r'^filings/<slug:symbol>/<slug:filingType>/(?P<slug>[\w.]*)/$', viewsFilings.viewFiling, name='viewFiling'),
    re_path(r'^filings/<slug:symbol>/<slug:filingType>/(?P<slug>[\w]*[.htm]+)/$', viewsFilings.viewFiling, name='viewFiling'),
    re_path(r'^filings/<slug:symbol>/<slug:filingType>/(?P<slug>[-\w.]*)/$', viewsFilings.viewFiling, name='viewFiling'),
    re_path(r'^filings/<slug:symbol>/<slug:filingType>/(?P<slug>[-\w]*[.htm]+)/$', viewsFilings.viewFiling, name='viewFiling'),

    re_path(r'^filings/<slug:symbol>/<slug:filingType>/(?P<fileName>[\w]*)\.(?P<fileExt>[\w]*)/$', viewsFilings.viewFiling, name='viewFiling'),
    re_path(r'^filings/<slug:symbol>/<slug:filingType>/(?P<fileName>[-\w]*)\.(?P<fileExt>[\w]*)/$', viewsFilings.viewFiling, name='viewFiling'),        

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)