from django.db.models import F, Q, When, Case, Value

from Groups.models import Group

from .models import Info, Messages, Friends, User


# VIEWS


def _update_unread_messages(request, rec_msgs, all_msgs, _type):
    if _type == "User":
        filtrd_rec_msgs = rec_msgs.filter(read=False)
        no_unread_msgs = filtrd_rec_msgs.count()
        request.user.info.unread_messages -= no_unread_msgs
        request.user.info.save()
        unread_id = filtrd_rec_msgs.first().id if no_unread_msgs else None
        rec_msgs.update(read=True)
    else:
        unread_msgs = all_msgs.exclude(read_by__id=request.user.id)
        no_unread_msgs = unread_msgs.count()
        request.user.info.unread_messages -= no_unread_msgs
        request.user.info.save()
        unread_id = unread_msgs.first().id if no_unread_msgs else None
        request.user.read_messages.add(*unread_msgs)
    return unread_id


def _send_message(request, form, rec_user, _type):
    if _type == "User":
        new_message = form.save(commit=False)
        new_message.sender, new_message.receiver = request.user, rec_user
        new_message.save()
        rec_user.info.unread_messages += 1
        rec_user.info.save()
    else:
        new_message = form.save(commit=False)
        new_message.sender, new_message.grp_receiver, new_message.read = request.user, rec_user, True
        new_message.save()
        g_members = rec_user.members.all()
        Info.objects.exclude(user=request.user).filter(user__in=g_members).update(
            unread_messages=F("unread_messages")+1)
        new_message.read_by.add(request.user)


def _assign_type_variables(request, _type, rec_id):
    rec_msgs = Messages.objects.none()
    grp_members = User.objects.none()
    if _type == "User":
        rec_user = User.objects.get(id=rec_id)
        sent_msgs = Messages.objects.filter(
            sender=request.user, receiver=rec_user)
        rec_msgs = Messages.objects.filter(
            sender=rec_user, receiver=request.user)
        all_msgs = (sent_msgs | rec_msgs).order_by("date_sent")
    elif _type == "Group":
        rec_user = Group.objects.get(id=rec_id)
        date_join_group = request.user.membership_set.get(
            group=rec_user).date_joined
        all_msgs = rec_user.grp_receiver.filter(date_sent__gte=date_join_group)
        # all_msgs = rec_user.grp_receiver.all()
        members = rec_user.members.all().exclude(
            username=request.user.username).order_by("-username")
        friends = Friends.get_friends(Friends, request.user)

        # Friends should come first when showing group members
        friends_id = friends.values_list("id", flat=True)
        priority = Case(
            When(id__in=friends_id, then=Value(1)),
            default=Value(2)
        )
        grp_members = members.annotate(
            position=priority).order_by("position", "username")
    return rec_msgs, rec_user, all_msgs, grp_members
