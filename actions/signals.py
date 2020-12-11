from django.db.models.signals import post_save
from django.dispatch import receiver
from actions.models import Actions
from actions.tasks import action_flag_2


@receiver(post_save, sender=Actions)
def do_action(sender, instance, **kwargs):
    action_flag_2(instance.driver, instance.start_event)
