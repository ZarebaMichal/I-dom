from django.urls import path, include, re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('register/', views.register_list),
    path('register/<int:pk>', views.register_detail),
    re_path(r'^api-logout/(?P<token>[a-zA-Z0-9]+)', views.logout_user),
]

urlpatterns = format_suffix_patterns(urlpatterns)
