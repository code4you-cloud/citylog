from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('freeweb/', views.create_report, name='create_report'),
    path('success/', views.report_success, name='report_success'),
    path("list/", views.ReportListView.as_view(), name="report_list"),
]
