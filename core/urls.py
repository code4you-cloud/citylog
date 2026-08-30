from django.urls import path
from . import views
#from .views import HomePage, RifiutiListView, RifiutiDetailView, DonazioniView, \
#    ManifestoView, RegoleView, GuidaFotoView, TrasparenzaView, MotivazioniView, ApiView, StatisticheView, UserDashboardView, MachineLearningView, MappaSegnalazioniView #dashboard

app_name='core'

urlpatterns =[
    #path('',views.HomePage.as_view(), name='home'),
    path("",views.HomePage.as_view(), name='home'),
    #path("segnalazioni/", RifiutiListView.as_view(), name="segnalazioni-list"),
    #path("segnalazione/<int:pk>/", RifiutiDetailView.as_view(), name="segnalazione-detail"),
    path("donazioni/", views.DonazioniView.as_view(), name="donazioni-view"),
    path("manifesto/", views.ManifestoView.as_view(), name="manifesto-view"),
    path("regole/", views.RegoleView.as_view(), name="regole-view"),
    path("guida-foto/", views.GuidaFotoView.as_view(), name="guida-foto"),
    path("trasparenza/", views.TrasparenzaView.as_view(), name="trasparenza"),
    path("motivazioni/", views.MotivazioniView.as_view(), name="motivazioni"),
    path("api-docs/", views.ApiView.as_view(), name="api-view"),
    #path("statistiche/", StatisticheView.as_view(), name="statistiche-view"),
    path("dashboard/", views.UserDashboardView.as_view(), name="dashboard"),
    path('machine-learning/', views.MachineLearningView.as_view(), name='machine_learning'),

    #sostituisce workflow /var/www/html
    path('mappa/segnalazioni/', views.MappaSegnalazioniView.as_view(), name='mappa_segnalazioni'),

    # URL specifici per app
    path('mappa/rifiuti/', views.MappaSegnalazioniView.as_view(), {'app_type': 'rifiuti'}, name='mappa_rifiuti'),
    path('mappa/ambiente/', views.MappaSegnalazioniView.as_view(), {'app_type': 'ambiente'}, name='mappa_ambiente'),
    path('mappa/strade/', views.MappaSegnalazioniView.as_view(), {'app_type': 'strade'}, name='mappa_strade'),

    #path("dashboard/", dashboard, name="dashboard"),
]
