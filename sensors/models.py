from django.db import models


class Sensors(models.Model):

    CATEGORIES = [
        ('temperature', 'temperature'),
        ('humidity', 'humidity'),
        ('gas', 'gas'),
        ('smoke', 'smoke'),
        ('water_temp', 'water_temp'),
    ]
    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=15, choices=CATEGORIES)
    battery_level = models.IntegerField(blank=True, null=True)
    notifications = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    frequency = models.IntegerField(default=300)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        verbose_name = "Sensor"
        verbose_name_plural = "Sensors"

    def __str__(self):
        return str(self.id)


class SensorsData(models.Model):
    sensor = models.ForeignKey(Sensors, on_delete=models.CASCADE)
    delivery_time = models.DateTimeField(auto_now_add=True)
    sensor_data = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Sensor data"
        verbose_name_plural = "Sensors data"

    def __str__(self):
        return f"{self.sensor.id}: {self.sensor.name}"
