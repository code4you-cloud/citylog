from django.urls import path
from .views import StatisticheDashboardView, StatisticheAPIView, AmbienteListView, AmbienteDetailView

app_name='ambiente'

urlpatterns =[
    # Dashboard principale (HTML)
    path("segnalazioni/", AmbienteListView.as_view(), name="segnalazioni-list"),
    path("segnalazione/<int:pk>/", AmbienteDetailView.as_view(), name="segnalazione-detail"),
    path('dashboard/', StatisticheDashboardView.as_view(), name='dashboard'),

    # API per aggiornamenti (JSON o HTML)
    path('api/', StatisticheAPIView.as_view(), name='api'),
]
