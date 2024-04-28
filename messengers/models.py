import uuid

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, When, Case, F, OuterRef, Subquery, Value

from django.core.validators import validate_image_file_extension

from Groups.models import Group

from .validators import (file_size_val, media_size_val, file_type_validator,
                         image_type_validator, Media, profile_val, media_ext_val)


def user_directory_media(instance, filename):
    extension = filename.split(".")[-1].lower()
    media_type = [typ_e for typ_e, ext in Media.items() if extension in ext][0]
    return f"USERS/{instance.sender.id}/Media/{media_type}/{filename}"


class Messages(models.Model):
    read = models.BooleanField(default=False)
    read_by = models.ManyToManyField(
        User, blank=True, related_name="read_messages")
    media = models.FileField(
        upload_to=user_directory_media, null=True, blank=True, validators=[media_ext_val, media_size_val, file_type_validator])
    text = models.TextField(blank=True, default="")
    date_sent = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver", null=True, blank=True)
    grp_receiver = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="grp_receiver", null=True, blank=True)

    def __str__(self):
        return self.media.name if self.media else self.text

    def delete(self):
        self.media.delete()
        super().delete()

    def media_type(self):
        if self.media:
            extension = self.media.url.split(".")[-1].lower()
            media_type = [typ_e for typ_e,
                          ext in Media.items() if extension in ext]
            return media_type[0]
        return False


def user_directory_path(instance, filename):
    return f"USERS/{instance.user.id}/Profile/{filename}"


class Info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=100, blank=True, default="")
    bio = models.CharField(max_length=200, blank=True, default="")
    prof_pics = models.ImageField(
        upload_to=user_directory_path, null=True, blank=True, validators=[validate_image_file_extension, image_type_validator, file_size_val, profile_val])
    unread_messages = models.IntegerField(default=0)
    notifications = models.IntegerField(default=0)

    def __str__(self):
        return self.bio if self.bio else f"{self.user.username}'s Info"


class Friends(models.Model):
    req_sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="req_sender")
    req_receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="req_receiver")
    status = models.BooleanField(default=False)
    sent_status = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    friend_date = models.DateTimeField(auto_now=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"{self.req_sender}_To_{self.req_receiver}"

    def check_request(self, sender, receiver):
        requests = self.objects.filter(
            models.Q(req_sender=sender, req_receiver=receiver, sent_status=True) |
            models.Q(req_sender=sender, req_receiver=receiver, status=True)
        )
        return requests.exists()

    def _message_date(x, user):
        if x.__class__.__name__ == "User":
            sent_msg = x.sender.filter(receiver=user)
            rec_msg = x.receiver.filter(sender=user)
            if sent_msg and rec_msg:
                sent_date = sent_msg.latest("date_sent").date_sent
                rec_date = rec_msg.latest("date_sent").date_sent
                return max([sent_date, rec_date])
            elif sent_msg:
                return sent_msg.latest("date_sent").date_sent
            elif rec_msg:
                return rec_msg.latest("date_sent").date_sent
            else:
                try:
                    return x.req_sender.filter(req_receiver=user)[0].friend_date
                except:
                    return x.req_receiver.filter(req_sender=user)[0].friend_date

        else:
            grp_rec_msg = x.grp_receiver.all()
            if grp_rec_msg:
                return grp_rec_msg.latest("date_sent").date_sent
            return user.membership_set.get(group=x).date_joined

    def _get_all_friends(self, user):
        user_friendships = self.objects.filter(
            Q(req_sender=user) |
            Q(req_receiver=user), status=True
        )
        friends = Case(
            When(req_sender=user, then=F('req_receiver')),
            default=F("req_sender")
        )
        user_friends_id = user_friendships.annotate(
            friend=friends).values_list("friend", flat=True)
        user_friends = User.objects.filter(id__in=user_friends_id)
        return user_friends

    def get_m_friends(self, user, exclude=False):
        last_message = Messages.objects.filter(
            Q(receiver=OuterRef("id"), sender=user) |
            Q(receiver=user, sender=OuterRef("id"))
        ).order_by("-date_sent")
        last_message_text = last_message.values_list("text", flat=True)[:1]
        last_message_media = last_message.values_list("media", flat=True)[:1]
        last_message_date = last_message.values_list(
            "date_sent", flat=True)[:1]

        user_friends = self._get_all_friends(self, user)
        user_friends = user_friends.annotate(
            model_name=Value("User"),
            last_text=Subquery(
                last_message_text, output_field=models.CharField()),
            last_media=Subquery(
                last_message_media, output_field=models.FileField()),
            last_date=Subquery(
                last_message_date, output_field=models.DateField())
        )

        grp_last_message = Messages.objects.filter(
            grp_receiver=OuterRef("id")).order_by("-date_sent")
        last_message_text = grp_last_message.values_list("text", flat=True)[:1]
        last_message_media = grp_last_message.values_list("media", flat=True)[
            :1]
        last_message_date = grp_last_message.values_list(
            "date_sent", flat=True)[:1]
        last_message_sender = grp_last_message.values_list(
            "sender__username", flat=True)[:1]
        groups = user.members.annotate(
            model_name=Value("Group"),
            last_text=Subquery(
                last_message_text, output_field=models.CharField()),
            last_media=Subquery(
                last_message_media, output_field=models.FileField()),
            last_date=Subquery(
                last_message_date, output_field=models.DateField()),
            last_sender=Subquery(
                last_message_sender, output_field=models.CharField()),
        )

        contacts = list(user_friends)+list(groups)
        sorted_contacts = sorted(
            contacts, key=lambda x: self._message_date(x, user), reverse=True)
        if not exclude or exclude not in sorted_contacts:
            return sorted_contacts
        sorted_contacts.remove(exclude)
        return sorted_contacts

    def get_friends(self, user, exclude=False):
        friendships = self.objects.filter(
            Q(req_sender=user) |
            Q(req_receiver=user),
            status=True
        )
        friends_case = Case(
            When(req_sender=user, then=F("req_receiver")),
            default=F("req_sender")
        )
        friends_id = friendships.annotate(
            friend=friends_case).values_list('friend', flat=True)
        friends = User.objects.filter(
            id__in=friends_id)
        if not exclude or exclude not in friends:
            return friends

        return friends.exclude(username=exclude.username)

    def get_room_name(self):
        name = f'{self.req_sender.username}_{self.req_receiver.username}{self.uuid}'
        return name