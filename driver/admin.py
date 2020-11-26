from django.contrib import admin
from django import forms
from driver.models import Drivers


class DriversCreationForm(forms.ModelForm):
    """A form for creating new drivers.
       Includes all the required fields
    """

    class Meta:
        model = Drivers
        fields = ('name', 'category', )


class DriversChangeForm(forms.ModelForm):
    """A form for updating drivers. Includes all the fields on
    the drivers.
    """

    class Meta:
        model = Drivers
        fields = ('name', 'category', 'is_active', 'ip_address', 'data',)


class DriversAdmin(admin.ModelAdmin):
    """
    Admin panel for driver. Shows all needed data.
    """

    model = Drivers
    list_display = ('name', 'id', 'category', 'is_active', 'ip_address',)
    list_filter = ('is_active', 'category',)
    search_fields = ('name',)


admin.site.register(Drivers, DriversAdmin)
