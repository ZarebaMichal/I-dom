from datetime import datetime
from celery.utils.log import get_task_logger
from celery import Celery
from rest_framework.response import Response
from rest_framework import status

from driver.models import Drivers

app = Celery('tasks', broker='amqp://')

logger = get_task_logger(__name__)


@app.task(name="action_flag_2")
def action_flag_2(driver, start):
    while start >= datetime.now().strftime('%H:%M'):
        try:
            driver_instance = Drivers.objects.get(name=driver)
        except Drivers.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        driver_instance.data = False
        driver_instance.save()
        logger.info("State changed")


