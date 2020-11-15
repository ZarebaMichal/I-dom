from django.urls import path
from . import views


urlpatterns = [
    # API paths
    path('drivers/list', views.list_of_drivers),
    path('drivers/add', views.add_driver),
    path('drivers/detail/<int:pk>', views.driver_detail),
    path('drivers/update/<int:pk>', views.update_driver),
    path('drivers/delete/<int:pk>', views.delete_driver),
    path('drivers/ip', views.add_driver_ip_address),
    path('drivers/action', views.send_action),
]