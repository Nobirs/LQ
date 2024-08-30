from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import CustomUser


@receiver(pre_save, sender=CustomUser)
def check_points(sender, instance, **kwargs):
    if instance.points >= 100:
        instance.increase_level()