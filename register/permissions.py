from django.core.exceptions import ObjectDoesNotExist
from rest_framework import permissions
from register.models import CustomUser


class IsUpdateProfile(permissions.BasePermission):

    def has_permission(self, request, view):
        # can write custom code
        # print view.kwargs
        try:
            user_profile = CustomUser.objects.get(
                pk=view.kwargs['pk'])
        except ObjectDoesNotExist:
            return False

        if request.user == user_profile:
            return True

        return False
