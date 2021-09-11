# taiwan_einvoice/urls.py
from django.urls import path

from . import views

app_name = 'taiwan_einvoice'
urlpatterns = [
    path('escpos_web/<int:escpos_web_id>/', views.escpos_web, name='escpos_web'),
    path('', views.index, name='index'),
]