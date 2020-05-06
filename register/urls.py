from django.urls import path, include

from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('register/', views.register_list),
    path('register/<int:pk>', views.register_detail),
]

urlpatterns = format_suffix_patterns(urlpatterns)
