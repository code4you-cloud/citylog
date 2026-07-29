from django.urls import path
from .views import StatisticheDashboardView, StatisticheAPIView, RifiutiListView, RifiutiDetailView

app_name='rifiuti'

urlpatterns =[
    # Dashboard principale (HTML)
    path("segnalazioni/", RifiutiListView.as_view(), name="segnalazioni-list"),
    path("segnalazione/<int:pk>/", RifiutiDetailView.as_view(), name="segnalazione-detail"),
    path('', StatisticheDashboardView.as_view(), name='dashboard'),

    # API per aggiornamenti (JSON o HTML)
    path('api/', StatisticheAPIView.as_view(), name='api'),
]
