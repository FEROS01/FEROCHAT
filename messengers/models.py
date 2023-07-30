from django.db import models
from django import forms
from django.contrib.auth.models import User
from datetime import datetime
from messenger import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, validate_image_file_extension
import magic

image = ["gif", "png", "jpeg", "jpg", "webp", "avif", "apng"]
video = ["mp4", "webm", "ogv"]
audio = ["mp3", "wav", "oga"]
document = ["pdf", "txt", "csv", "json",]
Media = {"image": image, "video": video, "audio": audio, "document": document}

media_extensions = image+video+document+audio
media_ext_val = FileExtensionValidator(
    media_extensions, "Unsupported File format", code="Invalid format")


def user_directory_media(instance, filename):
    extension = filename.split(".")[-1]
    media_type = [typ_e for typ_e, ext in Media.items() if extension in ext][0]
    return f"{instance.sender.username}/Media/{media_type}/{filename}"


def file_size_val(file):
    size = round(file.size/1_048_576, 2)
    file_name = file.name[0:15]+"...." if len(file.name) > 15 else file.name
    allowed_size = 10
    if size > allowed_size:
        raise ValidationError(
            f"{file_name} is greater than {allowed_size}MB", code="Invalid file size")


def file_type_validator(file):
    accept = [f"{media}/{exts}" for media, ext in Media.items()
              for exts in ext if media != "document"]
    accept += ["application/pdf",
               "application/json", "text/plain", "text/csv", "audio/mpeg"]
    extension = file.url.split(".")[-1]
    file_name = file.name[0:15]+"...." if len(file.name) > 15 else file.name
    if extension not in audio:
        file_mime_type = magic.from_buffer(file.read(1024), mime=True)
        if file_mime_type not in accept:
            raise ValidationError(
                f" {file_name} is an unsupported file type '{file_mime_type}'", code="Invalid Format")


class Messages(models.Model):
    read = models.BooleanField(default=True)
    media = models.FileField(
        upload_to=user_directory_media, null=True, blank=True, validators=[media_ext_val, file_size_val, file_type_validator])
    text = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sender")
    receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="receiver")

    def __str__(self):
        return self.text if self.text else self.media.name

    def delete(self):
        self.media.delete()
        super().delete()

    def media_type(self):
        extension = self.media.url.split(".")[-1]
        media_type = [typ_e for typ_e,
                      ext in Media.items() if extension in ext]
        return media_type[0]


def user_directory_path(instance, filename):
    return f"{instance.user.username}/Profile/{filename}"


def image_type_validator(file):
    accept = [f"image/{ext}" for ext in image]
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    if file_mime_type not in accept:
        raise ValidationError(f"Unsupported file type '{file_mime_type}'")


profile_val = FileExtensionValidator(
    image, "Unsupported file format. Try a valid image format")


class Info(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    about = models.CharField(max_length=100, blank=True, default="")
    bio = models.CharField(max_length=200, blank=True, default="")
    prof_pics = models.ImageField(
        upload_to=user_directory_path, null=True, blank=True, validators=[validate_image_file_extension, image_type_validator, file_size_val, profile_val])
    unread_messages = models.IntegerField(default=0)

    def __str__(self):
        return self.bio if self.bio else f"{self.user.username}'s Info"


class Friends(models.Model):
    req_sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="req_sender")
    req_receiver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="req_receiver")
    status = models.BooleanField(default=False)
    sent_status = models.BooleanField(default=False)
    date_added = models.DateTimeField(auto_now_add=True)
    friend_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.req_sender}_To_{self.req_receiver}"

    def check_request(self, sender, receiver):
        try:
            self.objects.get(req_sender=sender, req_receiver=receiver)
            return True
        except:
            return False

    def _last_message(x, user):
        sent_msg = x.sender.filter(receiver=user)
        rec_msg = x.receiver.filter(sender=user)
        if sent_msg and rec_msg:
            sent_date = sent_msg.latest("date_added").date_added
            rec_date = rec_msg.latest("date_added").date_added
            return max([sent_date, rec_date])
        elif sent_msg:
            return sent_msg.latest("date_added").date_added
        elif rec_msg:
            return rec_msg.latest("date_added").date_added
        else:
            try:
                return x.req_sender.filter(req_receiver=user)[0].friend_date
            except:
                return x.req_receiver.filter(req_sender=user)[0].friend_date
        # sent_msg = x.sender.latest('date_added').date_added
        # rec_msg = x.receiver.latest('date_added').date_added
        # return max([sent_msg, rec_msg])

    def _get_all_friends(self, user):
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

    def get_m_friends(self, user, exclude=False):
        user_friends = self._get_all_friends(self, user)
        lis_t = sorted(
            user_friends, key=lambda x: self._last_message(x, user), reverse=True)
        if not exclude or exclude not in lis_t:
            return lis_t
        lis_t.remove(exclude)
        return lis_t

    def get_friends(self, user, exclude=False):
        user_friends = self._get_all_friends(self, user)
        lis_t = sorted(user_friends, key=lambda x: x.username)
        if not exclude or exclude not in lis_t:
            return lis_t
        lis_t.remove(exclude)
        return lis_t


def group_directory_path(instance, filename):
    return f"{instance.name.upper()}/Profile/{filename}"


class Group(models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(blank=True, max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    admins = models.ManyToManyField(
        User, related_name="admins")
    prof_pics = models.ImageField(
        upload_to=group_directory_path, null=True, blank=True)
    members = models.ManyToManyField(
        User,
        through="Membership",
        through_fields=("group", "member"),
        related_name="members"
    )

    def __str__(self):
        return self.name


class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    inviter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="inviter")

    def __str__(self):
        return f"{self.group.name}_{self.user.username}"
