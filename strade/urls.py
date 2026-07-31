from django.urls import path
from .views import StatisticheDashboardView, StatisticheAPIView, StradeListView, StradeDetailView

app_name='strade'

urlpatterns =[
    # Dashboard principale (HTML)
    path("segnalazioni/", StradeListView.as_view(), name="segnalazioni-list"),
    path("segnalazione/<int:pk>/", StradeDetailView.as_view(), name="segnalazione-detail"),
    path('dashboard/', StatisticheDashboardView.as_view(), name='dashboard'),

    # API per aggiornamenti (JSON o HTML)
    path('api/', StatisticheAPIView.as_view(), name='api'),
]
