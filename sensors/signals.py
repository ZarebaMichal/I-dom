from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from sensors.models import Sensors, SensorsData
import actions.tasks


@receiver(pre_save, sender=SensorsData)
def send_to_tasks(sender, instance, **kwargs):
    actions.tasks.prep_for_async_tasks_3_and_4.delay(instance.sensor.name, instance.sensor_data)


@receiver(post_save, sender=SensorsData)
def change_frequency(sender, instance, **kwargs):
    actions.tasks.async_change_frequency.delay(instance.sensor.name)


@receiver(pre_save, sender=SensorsData)
def push_notifications(sender, instance, **kwargs):
    actions.tasks.async_push_notifications.delay(instance.sensor.name)


@receiver(pre_save, sender=SensorsData)
def sms_notifications(sender, instance, **kwargs):
    actions.tasks.async_sms_notifications.delay(instance.sensor.name)


@receiver(post_save, sender=Sensors)
def low_battery_level(sender, instance, **kwargs):
    actions.tasks.async_low_battery_level_notification.delay(instance.name)
