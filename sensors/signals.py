from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.dispatch import receiver
from requests import Response

from sensors.models import Sensors
import requests


@receiver(pre_save, sender=Sensors)
def do_something_if_changed(sender, instance, **kwargs):
    try:
        sensor = Sensors.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        pass # Object is new, so field hasn't technically changed, but you may want to do something else here.
    else:
        if not sensor.frequency == instance.frequency: # Field has changed
            # do something
            data_for_sensor = {
                #'id': sensor.id,
                'name': sensor.name,
                'frequency': instance.frequency
            }
            try:
                response = requests.post(f'http://{sensor.ip_address}:8000/receive', data=data_for_sensor)
                response.raise_for_status()
            except requests.exceptions.ConnectionError:
                print('Service offline')

            except requests.exceptions.Timeout:
                print('Timeout')
