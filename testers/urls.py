from django.urls import path
from .views import RegisterTesterView, SuccessView

app_name = 'testers'

urlpatterns = [
    path('', RegisterTesterView.as_view(), name='register'),
    path('grazie/', SuccessView.as_view(), name='success'),
]
