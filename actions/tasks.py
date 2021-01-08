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


@shared_task(name="prep_for_async_tasks_3_and_4")
def prep_for_async_tasks_3_and_4(sensor, sensor_data):
    logger.info("Let's check if there is any falg 3 and 4 task to do!")
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
