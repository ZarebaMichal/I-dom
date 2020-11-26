from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Sensors, SensorsData


class SensorsCreationForm(forms.ModelForm):
    """A form for creating new sensors.
       Includes all the required
    """

    class Meta:
        model = Sensors
        fields = ('name', 'category', 'frequency')


class SensorsChangeForm(forms.ModelForm):
    """A form for updating sensors. Includes all the fields on
    the sensor
    """

    class Meta:
        model = Sensors
        fields = ('name', 'category', 'frequency', 'notifications', 'is_active', 'ip_address')


class SensorAdmin(admin.ModelAdmin):
    """
    Panel admin for sensors displaying all data needed.
    """

    model = Sensors
    list_display = ('name', 'id', 'category', 'notifications', 'is_active', 'frequency', 'ip_address')
    list_filter = ('is_active', 'category', 'notifications',)
    search_fields = ('name', 'category',)


admin.site.register(Sensors, SensorAdmin)


class SensorsDataCreationForm(forms.ModelForm):
    """A form for creating new sensors data.
       Includes all the required fields
    """

    class Meta:
        model = SensorsData
        fields = ('sensor', 'sensor_data')


class SensorsDataChangeForm(forms.ModelForm):
    """A form for updating sensors data. Includes all the fields on
    the sensors data
    """

    class Meta:
        model = SensorsData
        fields = ('sensor_data',)


class SensorDataAdmin(admin.ModelAdmin):
    """
    Panel for sensor data model. Includes sensor name instead of id.
    """
    list_display = ('sensor_name', 'sensor_data', 'delivery_time',)

    def sensor_name(self, obj):
        return obj.sensor.name
    model = SensorsData

    list_filter = ('sensor',)

admin.site.register(SensorsData, SensorDataAdmin)