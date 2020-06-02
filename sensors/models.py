from django.db import models
from django.utils import timezone


class Sensors(models.Model):

    CATEGORIES = [
        ('temperature', 'temperature'),
        ('humidity', 'humidity'),
    ]
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=15, choices=CATEGORIES)
    battery_level = models.IntegerField(blank=True, null=True)
    notifications = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.id


class SensorsData(models.Model):
    sensor_id = models.ForeignKey(Sensors, on_delete=models.CASCADE)
    delivery_time = models.DateTimeField(default=timezone.now)
    sensor_data = models.CharField(max_length=20)
