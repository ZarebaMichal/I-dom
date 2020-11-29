from django.db import models

from driver.models import Drivers
from sensors.models import Sensors
import json


class Actions(models.Model):

    id = models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    name = models.CharField(max_length=50, unique=True)
    sensor = models.ForeignKey(Sensors, on_delete=models.CASCADE, blank=True, null=True)
    trigger = models.IntegerField(blank=True, null=True)
    operator = models.CharField(max_length=1, blank=True, null=True)
    driver = models.ForeignKey(Drivers, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    days = models.CharField(max_length=250)
    start_event = models.TimeField()
    end_event = models.TimeField(blank=True, null=True)
    action = models.CharField(max_length=50)
    flag = models.IntegerField()

    def set_days(self, x):
        self.days = json.dumps(x)

    def get_days(self):
        return json.loads(self.days)

    def set_action(self, x):
        self.action = json.dumps(x)

    def get_action(self):
        return json.loads(self.action)

    class Meta:
        verbose_name = "Action"
        verbose_name_plural = "Actions"

    def __str__(self):
        return self.name
