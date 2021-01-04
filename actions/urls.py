from django.urls import path
from . import views


urlpatterns = [
    # API paths
    path('actions/list', views.list_of_actions),
    path('actions/add', views.add_action),
    path('actions/detail/<int:pk>', views.action_detail),
    path('actions/update/<int:pk>', views.update_action),
    path('actions/delete/<int:pk>', views.delete_action),
]
