from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from fcm_django.models import FCMDevice
from register.models import CustomUser
from pyfcm import FCMNotification
from decouple import config
from twilio.rest import Client
from sensors.models import Sensors, SensorsData
import requests


@receiver(pre_save, sender=Sensors)
def do_something_if_changed(sender, instance, **kwargs):
    try:
        sensor = Sensors.objects.get(pk=instance.pk)
    except ObjectDoesNotExist:
        return 'Sensor doesnt exists'
    else:
        if not sensor.frequency == instance.frequency:  # Field has changed
            data_for_sensor = {
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


@receiver(pre_save, sender=SensorsData)
def push_notifications(sender, instance, **kwargs):
    try:
        sensor = Sensors.objects.get(pk=instance.sensor_id)
    except ObjectDoesNotExist:
        pass  # Object is new, so field hasn't technically changed, but you may want to do something else here.
    else:
        if sensor.category == 'smoke':
            element = 'dym'
        elif sensor.category == 'gas':
            element = 'gaz'
        elif sensor.category == 'rain_sensor':
            element = 'deszcz'
        categories = ['smoke', 'gas', 'rain_sensor']

        if sensor.notifications and sensor.category in categories:
            push_service = FCMNotification(api_key=config('FCM_APIKEY'))

            fcm_token = [obj.registration_id for obj in FCMDevice.objects.filter(active=True)]

            # ToDo: Different message depending on user language field
            message_title = f"Czujnik {sensor.name} wykrył {element}"
            message_body = f"Czujnik {sensor.name} wykrył {element}. Uważaj na siebie!"
            result = push_service.notify_multiple_devices(registration_ids=fcm_token,
                                                          message_title=message_title,
                                                          message_body=message_body,
                                                          click_action="FLUTTER_NOTIFICATION_CLICK",
                                                          android_channel_id="flutter.idom/notifications")


@receiver(pre_save, sender=SensorsData)
def sms_notifications(sender, instance, **kwargs):

    try:
        sensor = Sensors.objects.get(pk=instance.sensor_id)
    except ObjectDoesNotExist:
        return "Sensors doesn't exists"
    else:
        d = {
                'gas': 'gaz',
                'smoke': 'dym',
                'rain_sensor': ['rain', 'deszcz']
            }

        categories = ['smoke', 'gas', 'rain_sensor']

        if sensor.notifications and sensor.category in categories:
            # Get users with sms notifications turned ON and with telephone number
            try:
                users = CustomUser.objects.exclude(sms_notifications=False)\
                                          .exclude(telephone='')\
                                          .exclude(telephone__isnull=True)
            except ObjectDoesNotExist:
                return 'No users with notifications turned ON'

            # Convert users objects to list
            users_list = list(users)
            # Load Twilio client
            client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))

            # Iterate over users to send them SMS
            for user in users_list:
                if user.language == 'pl':
                    element = d['rain_sensor'][1] if sensor.category == 'rain_sensor' else d[sensor.category]
                    body = f"Czujnik {sensor.name} wykrył {element}"
                elif user.language == 'eng':
                    element = d['rain_sensor'][0] if sensor.category == 'rain_sensor' else sensor.category
                    body = f"Sensor {sensor.name} detected {element}"

                client.messages \
                      .create(
                          body=body,
                          from_=config('TWILIO_NUMBER'),
                          to=str(user.telephone)
                             )


@receiver(post_save, sender=Sensors)
def low_battery_level(sender, instance, **kwargs):
    try:
        sensor = Sensors.objects.get(pk=instance.id)
    except ObjectDoesNotExist:
        return "Sensor doesn't exists"

    else:
        if sensor.battery_level is not None and sensor.battery_level in (10, 20, 30) and sensor.notifications:
            push_service = FCMNotification(api_key=config('FCM_APIKEY'))
            fcm_token = [obj.registration_id for obj in FCMDevice.objects.filter(active=True)]

            # ToDo: Different messages depending on user language field
            message_title = f"W czujniku {sensor.name} jest niski poziom baterii, {sensor.battery_level} %"
            message_body = f"W czujniku {sensor.name} jest niski poziom baterii, {sensor.battery_level} %"
            result = push_service.notify_multiple_devices(registration_ids=fcm_token,
                                                          message_title=message_title,
                                                          message_body=message_body,
                                                          click_action="FLUTTER_NOTIFICATION_CLICK",
                                                          android_channel_id="flutter.idom/notifications")
