from django.urls import path, include, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views


urlpatterns = [
    # API paths
    path('sensors/', views.all_sensors),
    path('sensors/<int:pk>', views.sensor_detail)
]