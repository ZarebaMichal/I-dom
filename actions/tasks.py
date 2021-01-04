from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery import shared_task
from my_application.celery import app
from rest_framework.response import Response
from rest_framework import status
from driver.models import Drivers
from yeelight import Bulb
from yeelight import BulbException
import requests


logger = get_task_logger(__name__)


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


@shared_task(name="action_flag_1")
def action_flag_1(driver: str, action: dict):
    logger.info("Let's start with this event!")
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
    elif driver_instance.category == 'clicker':
        turn_clicker(driver, action['status'])

    # ToDo: Other categories
    # driver_instance.data = False
    # driver_instance.save()
    logger.info("Event has been done on time!")
