from datetime import datetime
from celery.utils.log import get_task_logger
from celery import shared_task
from decouple import config
from django.core.exceptions import ObjectDoesNotExist
from fcm_django.models import FCMDevice
from pyfcm import FCMNotification
from actions.models import Actions
from rest_framework.response import Response
from rest_framework import status
from driver.models import Drivers
from yeelight import Bulb
from yeelight import BulbException
import requests
from register.models import CustomUser
from sensors.models import Sensors
from twilio.rest import Client


logger = get_task_logger(__name__)


def correct_value_check(trigger: int, operator: str, sensor_data: int):
    if operator == '>':
        return True if sensor_data > trigger else False
    elif operator == '<':
        return True if sensor_data < trigger else False
    elif operator == '=':
        return True if sensor_data == trigger else False


def turn_clicker(driver: str, action: bool):
    driver = Drivers.objects.get(name=driver)
    try:
        if action:
            result = requests.post(f'http://{driver.ip_address}/', data=1)
            result.raise_for_status()
            driver.data = True
        else:
            result = requests.post(f'http://{driver.ip_address}/', data=0)
            result.raise_for_status()
            driver.data = False
        driver.save()
        return True
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        driver.data = False
        driver.save()
        return False


def turn_bulb(driver: str, action: bool):
    bulb = Bulb(driver.ip_address)
    try:
        if action:
            bulb.turn_on()
            driver.data = True
        else:
            bulb.turn_off()
            driver.data = False
        driver.save()
        return True
    except BulbException:
        driver.data = False
        driver.save()
        return False


def set_brightness(driver: str, brightness: int):
    bulb = Bulb(driver.ip_address)
    try:
        bulb.set_brightness(brightness)
        return True
    except BulbException:
        driver.data = False
        driver.save()
        return False


def set_colours(driver: str, red: int, green: int, blue: int):
    bulb = Bulb(driver.ip_address)
    try:
        bulb.set_rgb(red, green, blue)
        return True
    except BulbException:
        driver.data = False
        driver.save()
        return False


@shared_task(name="make_action")
def make_action(action_name:str):
    logger.info("Let's start with this event with flag 3 or 4!")
    action = Actions.objects.get(name=action_name)
    if action.driver.category == 'bulb':
        if action.action['type'] == 'turn':
            turn_bulb(action.driver, action.action['status'])
        if action.action['type'] == 'brightness':
            turn_bulb(action.driver, True)
            set_brightness(action.driver, action['brightness'])
        if action.action['type'] == 'colour':
            turn_bulb(action.driver, True)
            set_colours(
                action.driver,
                action.action['red'],
                action.action['green'],
                action.action['blue'])
    elif action.driver.category == 'clicker' or action.driver.category == 'roller_blind':
        turn_clicker(action.driver, action.action['status'])
    logger.info("Event with flag 3 or 4 has been done on time!")


@shared_task(name="action_flag_1")
def action_flag_1(driver: str, action: dict):
    logger.info("Let's start with this event! (FLAG 1)")
    try:
        driver_instance = Drivers.objects.get(name=driver)
    except Drivers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if driver_instance.category == 'bulb':
        if action['type'] == 'turn':
            turn_bulb(driver_instance, action['status'])
        if action['type'] == 'brightness':
            turn_bulb(driver, True)
            set_brightness(driver_instance, action['brightness'])
        if action['type'] == 'colour':
            turn_bulb(driver_instance, True)
            set_colours(
                    driver_instance,
                    action['red'],
                    action['green'],
                    action['blue']
                    )
    elif driver_instance.category == 'clicker' or driver_instance.category == 'roller_blind':
        turn_clicker(driver_instance, action['status'])

    # driver_instance.data = False
    # driver_instance.save()
    logger.info("Event has been done on time! (FLAG 1)")


@shared_task(name="prep_for_async_tasks_3_and_4")
def prep_for_async_tasks_3_and_4(sensor_name:str, sensor_data:str):
    logger.info("Let's check if there is any falg 3 and 4 task to do!")
    try:
        sensor = Sensors.objects.get(name=sensor_name)
    except Sensors.DoesNotExist:
        return "There is no such sensor"
    try:
        actions_prep = Actions.objects \
            .select_related('sensor', 'driver') \
            .filter(
            is_active=True,
            flag=3,
            sensor=sensor.id
        )

        time = datetime.time(datetime.now())
        actions_prep_2 = Actions.objects \
            .select_related('sensor', 'driver') \
            .filter(
            is_active=True,
            flag=4,
            sensor=sensor.id,
            start_event__lt=time,
            end_event__gte=time
        )

        actions = [obj for obj in actions_prep if datetime.today().strftime('%w') in obj.days]
        actions2 = [obj for obj in actions_prep_2 if datetime.today().strftime('%w') in obj.days]
    except ObjectDoesNotExist:
        logger.info("There is nothing to do here!")
        return 'There is not such action'

    actions = actions + actions2

    for action in actions:
        if correct_value_check(int(action.trigger), action.operator, int(sensor_data)):
            make_action(str(action.name))


@shared_task(name="change_frequency")
def async_change_frequency(sensor_name:str):
    try:
        sensor = Sensors.objects.get(name=sensor_name)
    except ObjectDoesNotExist:
        return 'Sensor doesnt exists'
    else:
        if sensor.has_changed:
            data_for_sensor = {
                'name': sensor.name,
                'frequency': sensor.frequency
            }

            try:
                response = requests.post(f'http://{sensor.ip_address}:8000/receive', data=data_for_sensor)
                response.raise_for_status()
                sensor.has_changed = False
                sensor.save()
            except requests.exceptions.ConnectionError:
                print('Service offline')
                sensor.has_changed = True
                sensor.save()
            except requests.exceptions.Timeout:
                print('Timeout')
                sensor.has_changed = True
                sensor.save()


@shared_task(name="push_notifications")
def async_push_notifications(sensor_name:str):
    try:
        sensor = Sensors.objects.get(name=sensor_name)
    except ObjectDoesNotExist:
        pass
    else:
        d = {
            'gas': ['gas', 'gaz'],
            'smoke': ['smoke', 'dym'],
            'rain_sensor': ['rain', 'deszcz']
        }

        categories = ['smoke', 'gas', 'rain_sensor']

        if sensor.notifications and sensor.category in categories:
            push_service = FCMNotification(api_key=config('FCM_APIKEY'))

            pl_users_id = [obj.id for obj in CustomUser.objects.filter(language='pl')]
            eng_users_id = [obj.id for obj in CustomUser.objects.filter(language='eng')]

            pl_fcm_token = [obj.registration_id for obj in FCMDevice.objects.filter(active=True) if
                            obj.user_id in pl_users_id]
            eng_fcm_token = [obj.registration_id for obj in FCMDevice.objects.filter(active=True) if
                             obj.user_id in eng_users_id]

            message_title = f"Czujnik {sensor.name} wykrył {d[sensor.category][1]}"
            message_body = f"Czujnik {sensor.name} wykrył {d[sensor.category][1]}. Uważaj na siebie!"
            push_service.notify_multiple_devices(registration_ids=pl_fcm_token,
                                                 message_title=message_title,
                                                 message_body=message_body,
                                                 click_action="FLUTTER_NOTIFICATION_CLICK",
                                                 android_channel_id="flutter.idom/notifications")

            message_title = f"Sensor {sensor.name} detected {d[sensor.category][0]}"
            message_body = f"Sensor {sensor.name} detected {d[sensor.category][0]}. Watch out for yourself!"
            push_service.notify_multiple_devices(registration_ids=eng_fcm_token,
                                                 message_title=message_title,
                                                 message_body=message_body,
                                                 click_action="FLUTTER_NOTIFICATION_CLICK",
                                                 android_channel_id="flutter.idom/notifications")


@shared_task(name="sms_notifications")
def async_sms_notifications(sensor_name:str):
    try:
        sensor = Sensors.objects.get(name=sensor_name)
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


@shared_task(name="low_battery")
def async_low_battery_level_notification(sensor_name:str):
    try:
        sensor = Sensors.objects.get(name=sensor_name)
    except ObjectDoesNotExist:
        return "Sensor doesn't exists"

    else:
        if sensor.battery_level is not None and sensor.battery_level in (10, 20, 30) and sensor.notifications:
            push_service = FCMNotification(api_key=config('FCM_APIKEY'))

            pl_users_id = [obj.id for obj in CustomUser.objects.filter(language='pl')]
            eng_users_id = [obj.id for obj in CustomUser.objects.filter(language='eng')]

            pl_fcm_token = [obj.registration_id for obj in FCMDevice.objects.filter(active=True) if
                            obj.user_id in pl_users_id]
            eng_fcm_token = [obj.registration_id for obj in FCMDevice.objects.filter(active=True) if
                             obj.user_id in eng_users_id]

            message_title = f"W czujniku {sensor.name} jest niski poziom baterii"
            message_body = f"W czujniku {sensor.name} jest niski poziom baterii, {sensor.battery_level} %"
            result = push_service.notify_multiple_devices(registration_ids=pl_fcm_token,
                                                          message_title=message_title,
                                                          message_body=message_body,
                                                          click_action="FLUTTER_NOTIFICATION_CLICK",
                                                          android_channel_id="flutter.idom/notifications")

            message_title = f"Sensor {sensor.name} has low battery level {sensor.battery_level} %"
            message_body = f"Sensor {sensor.name} has low battery level, {sensor.battery_level} %"
            result = push_service.notify_multiple_devices(registration_ids=eng_fcm_token,
                                                          message_title=message_title,
                                                          message_body=message_body,
                                                          click_action="FLUTTER_NOTIFICATION_CLICK",
                                                          android_channel_id="flutter.idom/notifications")
