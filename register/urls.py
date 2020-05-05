from django.urls import path
from django.conf.urls import url, include
from . import views

urlpatterns = [
    path('register/', views.register_list, name='index')
]