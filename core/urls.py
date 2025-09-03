from django.urls import path
from .views import HomePage, RifiutiListView, RifiutiDetailView, DonazioniView, ManifestoView, RegoleView, ApiView, StatisticheView, dashboard

app_name='core'

urlpatterns =[
    #path('',views.HomePage.as_view(), name='home'),
    path("",HomePage.as_view(), name='home'),
    path("segnalazioni/", RifiutiListView.as_view(), name="segnalazioni-list"),
    path("segnalazione/<int:pk>/", RifiutiDetailView.as_view(), name="segnalazione-detail"),
    path("donazioni/", DonazioniView.as_view(), name="donazioni-view"),
    path("manifesto/", ManifestoView.as_view(), name="manifesto-view"),
    path("regole/", RegoleView.as_view(), name="regole-view"),
    path("api-docs/", ApiView.as_view(), name="api-view"),
    path("statistiche/", StatisticheView.as_view(), name="statistiche-view"),
    path("dashboard/", dashboard, name="dashboard"),
]
