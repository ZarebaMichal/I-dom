from datetime import datetime
from celery.utils.log import get_task_logger
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from actions.models import Actions
from rest_framework.response import Response
from rest_framework import status
from driver.models import Drivers
from yeelight import Bulb
from yeelight import BulbException
import requests

from sensors.models import Sensors

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
    driver = Drivers.objects.get(name=driver)
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
    driver = Drivers.objects.get(name=driver)
    bulb = Bulb(driver.ip_address)
    try:
        bulb.set_brightness(brightness)
        return True
    except BulbException:
        driver.data = False
        driver.save()
        return False


def set_colours(driver: str, red: int, green: int, blue: int):
    driver = Drivers.objects.get(name=driver)
    bulb = Bulb(driver.ip_address)
    try:
        bulb.set_rgb(red, green, blue)
        return True
    except BulbException:
        driver.data = False
        driver.save()
        return False


@shared_task(name="make_action")
def make_action(action, driver):
    if driver.category == 'bulb':
        if action['type'] == 'turn':
            turn_bulb(driver, action.action['status'])
        if action['type'] == 'brightness':
            turn_bulb(driver, True)
            set_brightness(driver, action.action['brightness'])
        if action['type'] == 'colour':
            turn_bulb(driver, True)
            set_colours(
                driver,
                action['red'],
                action['green'],
                action['blue'])
    elif driver.category == 'clicker' or driver.category == 'roller_blind':
        turn_clicker(driver, action['status'])


@shared_task(name="action_flag_1")
def action_flag_1(driver: str, action: dict):
    logger.info("Let's start with this event! (FLAG 1)")
    try:
        driver_instance = Drivers.objects.get(name=driver)
    except Drivers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if driver_instance.category == 'bulb':
        if action['type'] == 'turn':
            turn_bulb(driver, action['status'])
        if action['type'] == 'brightness':
            turn_bulb(driver, True)
            set_brightness(driver, action['brightness'])
        if action['type'] == 'colour':
            turn_bulb(driver, True)
            set_colours(
                    driver,
                    action['red'],
                    action['green'],
                    action['blue']
                    )
    elif driver_instance.category == 'clicker' or driver_instance.category == 'roller_blind':
        turn_clicker(driver, action['status'])

    # ToDo: Other categories
    # driver_instance.data = False
    # driver_instance.save()
    logger.info("Event has been done on time! (FLAG 1)")


# @shared_task(name="prep_for_async_tasks_3_and_4")
# def prep_for_async_tasks_3_and_4(sensor, sensor_data):
#     try:
#         # DevNote: Discuss with team about days in flag 3
#         actions_prep = Actions.objects.filter(is_active=True,
#                                          flag=3,
#                                          sensor=sensor.id)
#
#         actions = [obj for obj in actions_prep if datetime.today().strftime('%w') in obj.days]
#         print(f"{actions}")
#     except ObjectDoesNotExist:
#         return 'There is not such action'
#
#     for action in actions:
#         if correct_value_check(int(action.trigger), action.operator, sensor_data):
#             make_action.delay(action)
#
#     # time = datetime.time(datetime.now()).strftime('%H:%M')
#     #
#     # try:
#     #     # DevNote: Discuss with team about days in flag 4
#     #     actions = Actions.objects.filter(is_active=True,
#     #                                      flag=4,
#     #                                      sensor=instance.sensor.id,
#     #                                      days=int(datetime.today().strftime('%w')),
#     #                                      start_event__lt=time,
#     #                                      end_event__gt=time
#     #                                      )
#     #     print(f"{actions}")
#     #
#     # except ObjectDoesNotExist:
#     #     return 'There is not such action'
#     #
#     # for action in actions:
#     #     if correct_value_check(int(action.trigger), action.operator, int(instance.sensor_data)):
#     #         driver = Drivers.object.get(name=action.driver)
#     #         if driver.category == 'bulb':
#     #             if action.action['type'] == 'turn':
#     #                 turn_bulb(driver, action.action['status'])
#     #             if action.action['type'] == 'brightness':
#     #                 turn_bulb(driver, True)
#     #                 set_brightness(driver, action.action['brightness'])
#     #             if action.action['type'] == 'colour':
#     #                 turn_bulb(driver, True)
#     #                 set_colours(
#     #                     driver,
#     #                     action.action['red'],
#     #                     action.action['green'],
#     #                     action.action['blue']
#     #                 )
#     #         elif driver.category == 'clicker' or driver.category == 'roller_blind':
#     #             turn_clicker(driver, action.action['status'])
