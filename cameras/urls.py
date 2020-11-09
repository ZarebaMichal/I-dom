from django.urls import path, include, re_path
from . import views

urlpatterns = [
    # API paths
    path('cameras/list', views.list_of_cameras),
    path('cameras/add', views.add_cameras),
    path('cameras/detail/<int:pk>', views.camera_detail),
    path('cameras/update/<int:pk>', views.update_camera),
    path('cameras/delete/<int:pk>', views.delete_camera),
    path('cameras/ip', views.add_camera_ip_address),
    path('xd', views.index, name='index'),
    path('cameras/stream/<int:pk>', views.ip_cam, name='ip_cam'),
]