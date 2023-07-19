from django.db.models.signals import post_save
from django.dispatch import receiver
from messengers.models import User, Info


@receiver(post_save, sender=User)
def create_info(sender, instance, created, **kwargs):
    if created:
        Info.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_info(sender, instance, **kwargs):
    instance.info.save()
