from django.contrib import admin
from .models import Sensors, SensorsData

# Register your models here.
admin.site.register(Sensors)
admin.site.register(SensorsData)