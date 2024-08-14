import uuid

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import validate_image_file_extension

from messengers.validators import image_type_validator, file_size_val, profile_val


def group_directory_path(instance, filename):
    return f"GROUPS/{instance.id}/Profile/{filename}"


class Group(models.Model):
    name = models.CharField(max_length=15)
    description = models.CharField(blank=True, max_length=100)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    admins = models.ManyToManyField(
        User, related_name="admins")
    prof_pics = models.ImageField(
        upload_to=group_directory_path, null=True, blank=True,
        validators=[validate_image_file_extension, image_type_validator, file_size_val, profile_val])
    members = models.ManyToManyField(
        User,
        through="Membership",
        through_fields=("group", "member"),
        related_name="members"
    )
    uuid = models.UUIDField(unique=True,default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.name


class Membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    inviter = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="inviter")
    uuid = models.UUIDField(unique=True,default=uuid.uuid4, editable=False)

    def get_room_name(self):
        room_name = f"G{self.uuid}"
        return room_name

    def __str__(self):
        return f"{self.group.name}_{self.member.username}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['group', 'member'], name="unique_membership")
        ]
