from django.urls import path
from . import views

app_name='core'

urlpatterns =[
    path('',views.HomePage.as_view(), name='home'),
]
