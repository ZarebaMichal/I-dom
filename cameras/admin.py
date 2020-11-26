from django.contrib import admin
from django import forms
from cameras.models import Cameras


class CamerasCreationForm(forms.ModelForm):
    """A form for creating new cameras.
       Includes all the required fields
    """

    class Meta:
        model = Cameras
        fields = ('name',)


class CamerasChangeForm(forms.ModelForm):
    """A form for updating cameras. Includes all the fields on
    the camera.
    """

    class Meta:
        model = Cameras
        fields = ('name', 'notifications', 'is_active', 'ip_address')


class CamerasAdmin(admin.ModelAdmin):
    """
    Admin panel for camera. Shows all needed data.
    """

    model = Cameras
    list_display = ('name', 'notifications', 'is_active', 'ip_address')
    list_filter = ('is_active', 'notifications',)
    search_fields = ('name',)


admin.site.register(Cameras, CamerasAdmin)
