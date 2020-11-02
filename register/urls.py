from django.conf.urls import url
from django.urls import path, include, re_path
from . import views
from fcm_django.api.rest_framework import FCMDeviceViewSet
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'devices', FCMDeviceViewSet)


urlpatterns = [
    # API paths
    path('users/list', views.users_list),
    path('users/add', views.register_user),
    path('users/detail/<str:username>', views.user_detail),
    path('users/update/<int:pk>', views.update_user),
    path('users/delete/<int:pk>', views.delete_user),
    re_path(r'^api-logout/(?P<token>[a-zA-Z0-9]+)$', views.logout_user),
    path(r'^', include(router.urls)),
]
