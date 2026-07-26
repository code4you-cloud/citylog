from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('freeweb/', views.create_report, name='create_report'),
    path('success/<int:report_id>/', views.report_success, name='report_success'),
    #path('success/', views.report_success, name='report_success'),
    path("list/", views.ReportListView.as_view(), name="report_list"),
    path("confirm/<int:report_id>/", views.confirm_report, name="confirm_report"),
    path("delete_report/<int:report_id>/", views.delete_report, name="delete_report"),
]
