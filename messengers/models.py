from django.db import models
from django.contrib.auth.models import User
# from django.contrib.auth.models import AbstractUser

# User.friends = []
# User.about = models.CharField(max_length=100)


class Messages(models.Model):
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver")

    def __str__(self):
        return self.text


class Info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=100, null=True, blank=True, default="")
    bio = models.TextField(null=True, blank=True, default="")

    def __str__(self):
        return self.bio

# class ReceivedMessages(models.Model):
#     text = models.TextField()
#     date_added = models.DateTimeField(auto_now_add=True)
#     receiver = models.ForeignKey(User, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.text
# Create your models here.
