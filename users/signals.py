from django.db.models.signals import post_save
from django.dispatch import receiver
from messengers.models import User, Info, Friends, Messages


@receiver(post_save, sender=User)
def create_info(sender, instance, created, **kwargs):
    if created:
        Info.objects.create(user=instance)
        FeroChat = User.objects.get(username='FeroChat')
        Friends.objects.create(req_sender=FeroChat,
                               req_receiver=instance, status=True)
        text = "Welcome to FEROCHAT messenger app! 🎉 Stay connected with friends and family, share moments, and chat effortlessly. We're thrilled to have you on board. Let the conversations begin!"
        Messages.objects.create(sender=FeroChat, receiver=instance, text=text)
        instance.info.unread_messages += 1
        instance.info.save()


@receiver(post_save, sender=User)
def save_info(sender, instance, **kwargs):
    instance.info.save()
