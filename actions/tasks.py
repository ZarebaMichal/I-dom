from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery import shared_task
from my_application.celery import app
from rest_framework.response import Response
from rest_framework import status
from driver.models import Drivers


logger = get_task_logger(__name__)


@shared_task(name="action_flag_1")
def action_flag_1(data):
    logger.info("Let's start with this event!")
    try:
        driver_instance = Drivers.objects.get(name=data[0])
    except Drivers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    driver_instance.data = False
    driver_instance.save()
    logger.info("Event has been done on time!")
