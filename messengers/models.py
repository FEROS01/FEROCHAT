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

# add date time field


class Friends(models.Model):
    req_sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="req_sender")
    req_receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="req_receiver")
    status = models.BooleanField(default=False)
    sent_status = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.req_sender}_To_{self.req_receiver}"

    def requests(self):
        f_requests = self.objects.filter(sent_status=True)
        pend_users = []
        for request in f_requests:
            if request.req_sender not in pend_users:
                pend_users.append(request.req_sender)
            if request.req_receiver not in pend_users:
                pend_users.append(request.req_receiver)

        return pend_users

    def get_friends(self, user):
        friends = self.objects.all()
        user_friends1 = friends.filter(req_sender=user)
        user_friends2 = friends.filter(req_receiver=user)
        friends = (user_friends1 | user_friends2).filter(status=True)
        user_friends = []
        for friend in friends:
            if friend.req_sender != user:
                user_friends.append(friend.req_sender)
            if friend.req_receiver != user:
                user_friends.append(friend.req_receiver)
        return user_friends
