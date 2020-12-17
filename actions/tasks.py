from celery.utils.log import get_task_logger
from celery.schedules import crontab
from my_application.celery import app
from rest_framework.response import Response
from rest_framework import status
from driver.models import Drivers


logger = get_task_logger(__name__)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, instance, **kwargs):
    time = instance.data['start_event'].split(':')
    sender.add_periodic_task(
        crontab(hour=time[0], minute=time[1], day_of_week=instance.data['days']),
        action_flag_1.s(instance.data['driver'])
    )


@app.task(name="action_flag_1")
def action_flag_1(driver):
    logger.info("Let's start with this event!")
    try:
        driver_instance = Drivers.objects.get(name=driver)
    except Drivers.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    driver_instance.data = False
    driver_instance.save()
    logger.info("Event has been done on time!")
