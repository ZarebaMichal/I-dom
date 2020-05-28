from django.urls import path, include, re_path
from . import views


urlpatterns = [
    # API paths
    path('sensors/list', views.list_of_sensors),
    path('sensors/add', views.add_sensors),
    path('sensors/detail/<int:pk>', views.sensor_detail),
    path('sensors/update/<int:pk>', views.update_sensor),
    path('sensors/delete/<int:pk>', views.delete_sensor)
]