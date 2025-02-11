from django.urls import path
from .views import HomePage, RifiutiListView, RifiutiDetailView, DonazioniView, ManifestoView

app_name='core'

urlpatterns =[
    #path('',views.HomePage.as_view(), name='home'),
    path("",HomePage.as_view(), name='home'),
    path("segnalazioni/", RifiutiListView.as_view(), name="segnalazioni-list"),
    path("segnalazione/<int:pk>/", RifiutiDetailView.as_view(), name="segnalazione-detail"),
    path("donazioni/", DonazioniView.as_view(), name="donazioni-view"),
    path("manifesto/", ManifestoView.as_view(), name="manifesto-view"),
]
