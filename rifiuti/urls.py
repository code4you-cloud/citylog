from django.urls import path
from .views import StatisticheDashboardView, StatisticheAPIView

app_name='rifiuti'

urlpatterns =[
    # Dashboard principale (HTML)
    path('', StatisticheDashboardView.as_view(), name='dashboard'),

    # API per aggiornamenti (JSON o HTML)
    path('api/', StatisticheAPIView.as_view(), name='api'),
]
