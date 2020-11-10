from django.core.exceptions import ObjectDoesNotExist
from django.db.models.signals import pre_save
from django.dispatch import receiver
from decouple import config
from requests import Response
from fcm_django.models import FCMDevice
from my_application.settings import FCM_SERVER_KEY
from register.models import CustomUser
from pyfcm import FCMNotification
from twilio.rest import Client
from decouple import config


from sensors.models import Sensors, SensorsData
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


@receiver(pre_save, sender=SensorsData)
def push_notifications(sender, instance, **kwargs):
    try:
        sensor = Sensors.objects.get(pk=instance.sensor_id)
    except ObjectDoesNotExist:
        pass # Object is new, so field hasn't technically changed, but you may want to do something else here.
    else:
        if sensor.category == 'smoke':
            push_service = FCMNotification(api_key=config('FCM_APIKEY'))

            fcm_token = []
            for obj in FCMDevice.objects.all():
                fcm_token.append(obj.registration_id)

            message_title = "W domu pojawil sie dym"
            message_body = "W domu pojawil sie dym, opusc mieszkanie i wezwij sluzby ratunkowe"
            result = push_service.notify_multiple_devices(registration_ids=fcm_token,
                                                          message_title=message_title,
                                                          message_body=message_body,
                                                          click_action="FLUTTER_NOTIFICATION_CLICK",
                                                          android_channel_id="flutter.idom/notifications")
            print(result)
        elif sensor.category == 'gas':
            push_service = FCMNotification(api_key=config('FCM_APIKEY'))

            fcm_token = []
            for obj in FCMDevice.objects.all():
                fcm_token.append(obj.registration_id)

            message_title = "W domu pojawil sie gaz"
            message_body = "W domu pojawil sie gaz, otworz okna, opusc mieszkanie i wezwij sluzby ratunkowe"
            result = push_service.notify_multiple_devices(registration_ids=fcm_token, message_title=message_title,
                                                          message_body=message_body,
                                                          click_action="FLUTTER_NOTIFICATION_CLICK",
                                                          android_channel_id="flutter.idom/notifications")
            print(result)


@receiver(pre_save, sender=SensorsData)
def sms_notifications(sender, instance, **kwargs):
    try:
        sensor = Sensors.objects.get(pk=instance.sensor_id)
    except ObjectDoesNotExist:
        pass  # Object is new, so field hasn't technically changed, but you may want to do something else here.
    else:

        if sensor.category == 'smoke' or sensor.category == 'gas':

            # Get users with sms notifications turned ON
            try:
                users = CustomUser.objects.filter(sms_notifications=True)
            except ObjectDoesNotExist:
                return 'No users with notficiations turned ON'

            # Conver users objects to list
            users_list = list(users)

            # Load Twilio client
            client = Client(config('TWILIO_ACCOUNT_SID'), config('TWILIO_AUTH_TOKEN'))

           # Iterate over users to send them SMS
            for user in users_list:
                # MySQL keeps empty records as str
                if type(user.telephone) is not str:
                    message = client.messages \
                                    .create(
                                        body="Wykryto gaz w Twoim mieszkaniu, TEST FROM IDOM",
                                        from_=config('TWILIO_NUMBER'),
                                        to='str(user.telephone)'
                                            )

