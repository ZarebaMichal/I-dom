from django.db.models.signals import pre_save
from django.dispatch import receiver
from actions.models import Actions
from django_celery_beat.models import CrontabSchedule, PeriodicTask
from actions.tasks import action_flag_1


@receiver(pre_save, sender=Actions)
def send_task_to_db(sender, instance, **kwargs):
    s_hours = instance.start_event.hour
    s_minutes = instance.start_event.minute
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute=s_minutes,
        hour=s_hours,
        day_of_week=instance.days,
        day_of_month='*',
        month_of_year='*',
    )
