from django.shortcuts import render, redirect
from django.db.models import F, Q
from django.contrib.auth.models import User
from django.contrib import messages as Msg
from .models import Messages, Friends, Group, Info, Membership
from .form import NewMessage, Search, SearchMessages
from datetime import datetime
from messenger.settings import TIME_ZONE
import pytz
timezone = pytz.timezone(TIME_ZONE)
# Create your views here.


def index(request):
    return render(request, "messengers/index.html")


def user_bio(request, user_id, _type):
    user_friends = Friends.get_friends(Friends, request.user)
    if _type == "User":
        user_bio = User.objects.get(id=user_id)
        bio_friends = Friends.get_friends(
            Friends, user_bio, exclude=request.user)
        mutual_friends = bio_friends.intersection(user_friends)
        other_friends = bio_friends.difference(user_friends)
        context = {
            "user_bio": user_bio, "bio_friends": bio_friends,
            "user_friends": user_friends, "mutual_friends": mutual_friends, "other_friends": other_friends, "type": _type
        }
    else:
        group_bio = Group.objects.get(id=user_id)
        all_members = group_bio.members.all()
        no_members = all_members.count()
        admins2 = group_bio.admins.all()
        memberships = Membership.objects.filter(
            group=group_bio).order_by("-date_joined")
        admins_memberships = memberships.filter(member__in=admins2)
        j_members = all_members.difference(admins2)
        frnd_members = j_members.intersection(user_friends)
        friend_members = sorted(list(j_members.intersection(
            user_friends)), key=lambda x: x.username)
        other_members = sorted(list(j_members.difference(
            frnd_members)), key=lambda x: x.username)
        members = friend_members+other_members
        context = {
            "user_bio": group_bio, "members": members, "no_members": no_members, "type": _type, "admins": admins2, "admins_mem": admins_memberships, "user_friends": user_friends, "creator": group_bio.creator
        }
    return render(request, "messengers/user_bio.html", context)


def users(request):
    users = User.objects.all()
    friends = Friends.get_friends(Friends, request.user)
    searched = False
    if request.method != "POST":
        form = Search()
    else:
        form = Search(data=request.POST)
        if form.is_valid():
            searched = True
            data = form.cleaned_data
            for user in users:
                search = data["search"].lower()
                name = [user.username.lower().startswith(search), user.last_name.lower(
                ).startswith(search), user.first_name.lower().startswith(search)]
                if not any(name):
                    users = users.exclude(id=user.id)
    context = {"users": users, "friends": friends,
               "form": form, "searched": searched}
    return render(request, "messengers/users.html", context)


def _search(searched, query_set):
    for msg in query_set:
        mesg = msg.text.lower()
        if searched not in mesg:
            query_set = query_set.exclude(id=msg.id)
    return query_set


def messages(request):
    friends = Friends.get_m_friends(Friends, request.user)
    searched = False
    msgs = Messages.objects.filter(
        sender=request.user) | Messages.objects.filter(receiver=request.user)
    groups = []

    if request.method != "POST":
        form = SearchMessages()
    else:

        form = SearchMessages(data=request.POST)
        if form.is_valid():
            searched = True
            data = form.cleaned_data["search"].lower()
            groups = request.user.members.all()
            for group in groups:
                grp_msgs = group.grp_receiver.all()
                msgs = msgs | grp_msgs
            msgs = msgs.order_by("-date_sent")
            msgs = _search(data, msgs)
    context = {"friends": friends, "form": form,
               "message_s": msgs, "searched": searched}
    return render(request, "messengers/messages.html", context)


def _update_unread_messages(request, rec_msgs, grp_msgs, unread_id, count, searched, _type):
    searched = False
    if _type == "User":
        filtrd_rec_msgs = rec_msgs.filter(read=False)
        no_unread_msgs = filtrd_rec_msgs.count()
        request.user.info.unread_messages -= no_unread_msgs
        request.user.info.save()
        unread_id = filtrd_rec_msgs.first().id if no_unread_msgs else None
        rec_msgs.update(read=True)
    else:
        filtrd_grp_rec_msgs = grp_msgs.exclude(read_by__id=request.user.id)
        no_unread_msgs = filtrd_grp_rec_msgs.count()
        request.user.info.unread_messages -= no_unread_msgs
        request.user.info.save()
        unread_id = filtrd_grp_rec_msgs.first().id if no_unread_msgs else None
        for mesg in grp_msgs:
            mesg.read_by.add(request.user)
            mesg.save()
    return searched, unread_id


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


def view_messages(request, rec_id, _type):
    unread_id, searched = None, True
    old_errors, count = [], 0
    sent_msgs = Messages.objects.none()
    rec_msgs = Messages.objects.none()
    grp_msgs = Messages.objects.none()
    grp_members = ""
    if _type == "User":
        rec_user = User.objects.get(id=rec_id)
        sent_msgs = Messages.objects.filter(
            sender=request.user, receiver=rec_user)
        rec_msgs = Messages.objects.filter(
            sender=rec_user, receiver=request.user)
        all_msgs = (sent_msgs | rec_msgs).order_by("date_sent")
    else:
        rec_user = Group.objects.get(id=rec_id)
        grp_msgs = rec_user.grp_receiver.all()
        members = rec_user.members.all().exclude(
            username=request.user.username).order_by("-username")
        friends = Friends.get_friends(Friends, request.user)
        for member in members:
            if member in friends:
                grp_members = f"{member.username} "+grp_members
            else:
                grp_members += f"{member.username} "

    if request.method != "POST":
        searched, unread_id = _update_unread_messages(
            request, rec_msgs, grp_msgs, unread_id, count, searched, _type)
        form = NewMessage()
        search_form = SearchMessages()
    elif "next" in request.POST:
        files = request.FILES.getlist('media')
        search_form = SearchMessages()
        if not files or len(files) == 1:
            form = NewMessage(request.POST, request.FILES)
            if form.is_valid():
                _send_message(request, form, rec_user, _type)
                return redirect("messengers:view_messages", rec_id=rec_id, _type=_type)
            old_errors.append(form.errors["media"])
        else:
            for file in files:
                request.FILES["media"] = file
                form = NewMessage(request.POST, request.FILES)
                if form.is_valid():
                    _send_message(request, form, rec_user, _type)
                else:
                    if form.errors["media"] not in old_errors:
                        old_errors.append(form.errors["media"])
    else:
        form = NewMessage()
        search_form = SearchMessages(request.POST)
        if search_form.is_valid():
            search_mesg = search_form.cleaned_data["search"].lower()
            all_msgs = all_msgs if _type == "User" else grp_msgs
            all_msgs = _search(search_mesg, all_msgs)
    all_msgs = all_msgs if _type == "User" else grp_msgs
    context = {
        "all_messages": all_msgs, "form": form, "search_form": search_form, "searched": searched, "rec_id": rec_id, "rec_user": rec_user,
        "unread_id": unread_id, "old_errors": old_errors, "type": _type, "members": grp_members
    }
    return render(request, "messengers/view_messages.html", context)


def delete_message(request, msg_id, rec_id, _type):
    try:
        message = Messages.objects.get(id=msg_id)
        if _type == "User":
            rec_user = User.objects.get(id=rec_id)
            if not message.read:
                rec_user.info.unread_messages -= 1
                rec_user.info.save()
        message.delete()
        return view_messages(request, rec_id, _type)
    except:
        return view_messages(request, rec_id, _type)


def send_request(request, rec_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    check_request = Friends.check_request(Friends, sender, receiver)
    if sender != receiver and not check_request:
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
        Msg.success(request, "Friend request sent!")
        request.user.info.notifications += 1
        receiver.info.notifications += 1
        receiver.info.save()
        request.user.info.save()
    return users(request)


def send_request_bio(request, rec_id, bio_id, _type):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    check_request = Friends.check_request(Friends, sender, receiver)
    if sender != receiver and not check_request:
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
        request.user.info.notifications += 1
        receiver.info.notifications += 1
        receiver.info.save()
        request.user.info.save()
        Msg.success(request, "Friend request sent!")
    return user_bio(request, bio_id, _type)


def cancel_request_bio(request, rec_id, bio_id, _type):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.filter(req_sender=sender, req_receiver=receiver,
                               sent_status=True).update(sent_status=False, friend_date=datetime.now(tz=timezone))
        Msg.success(request, "Friend request canceled!")
    return user_bio(request, bio_id, _type)


def cancel_request(request, rec_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.filter(req_sender=sender, req_receiver=receiver,
                               sent_status=True).update(sent_status=False, friend_date=datetime.now(tz=timezone))
        Msg.success(request, "Friend request canceled!")
    return users(request)


def notifications(request):
    fr_requests = Friends.objects.filter(
        Q(req_receiver=request.user) |
        Q(req_sender=request.user)
    ).order_by("-friend_date")
    request.user.info.notifications = 0
    request.user.info.save()
    context = {"fr_requests": fr_requests}
    return render(request, "messengers/notifications.html", context)


def accept_request(request, sen_id):
    sender = User.objects.get(id=sen_id)
    receiver = request.user
    accepted = Friends.objects.filter(
        req_sender=sender, req_receiver=receiver, sent_status=True)
    if accepted.exists():
        accepted.update(status=True, sent_status=False,
                        friend_date=datetime.now(tz=timezone))
    sender.info.notifications += 1
    sender.info.save()
    Msg.success(request, "Friend request accepted!")
    return notifications(request)


def decline_request(request, sen_id):
    sender = User.objects.get(id=sen_id)
    receiver = request.user
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.filter(req_sender=sender, req_receiver=receiver, sent_status=True).update(
            sent_status=False, rejected=True, friend_date=datetime.now(tz=timezone))
        Msg.success(request, "Friend request declined!")
        sender.info.notifications += 1
        sender.info.save()
    return notifications(request)


def _search_friends(c_friends, searched, form, friends):
    searched = True
    data = form.cleaned_data
    for friend in c_friends:
        search = data["search"].lower()
        name = [friend.username.lower().startswith(search), friend.last_name.lower(
        ).startswith(search), friend.first_name.lower().startswith(search)]
        if not any(name):
            friends = friends.exclude(username=friend.username)
    return searched, friends


def friends(request, user_id):
    user = User.objects.get(id=user_id)
    friends = Friends.get_friends(Friends, user)
    c_friends = list(friends)
    searched = False
    if request.method != "POST":
        form = Search()
    else:
        form = Search(data=request.POST)
        if form.is_valid():
            searched, friends = _search_friends(
                c_friends, searched, form, friends)
    context = {"friends": friends, "searched": searched, "form": form}
    return render(request, "messengers/friends.html", context)


def unfriend(request, user_id, friend_id):
    friend = User.objects.get(id=friend_id)
    Friends.objects.filter(
        Q(req_sender=friend, req_receiver=request.user, status=True) |
        Q(req_sender=request.user, req_receiver=friend, status=True)
    ).delete()
    # try:
    #     Friends.objects.get(
    #         req_sender=friend, req_receiver=request.user).delete()
    # except:
    #     Friends.objects.get(
    #         req_sender=request.user, req_receiver=friend).delete()
    return friends(request, user_id)


def view_media(request, rec_id, _type):
    if _type == "User":
        receiver = User.objects.get(id=rec_id)
        # messages1 = Messages.objects.filter(
        #     sender=request.user, receiver=receiver)
        # messages2 = Messages.objects.filter(
        #     sender=receiver, receiver=request.user)
        messages = Messages.objects.filter(
            Q(sender=request.user, receiver=receiver) |
            Q(sender=receiver, receiver=request.user)
        ).order_by("-date_sent")
        print(messages)
        # messages = (messages1 | messages2).order_by("-date_sent")
        media_msgs = messages.exclude(
            Q(media__isnull=True) | Q(media__exact=""))
        print(media_msgs)
        # media_msgs = [message for message in messages if message.media]
    else:
        grp = Group.objects.get(id=rec_id)
        messages = grp.grp_receiver.all()
        media_msgs = messages.exclude(
            Q(media__isnull=True) | Q(media__exact=""))
    context = {"media_mesgs": media_msgs, "rec_id": rec_id, "type": _type}
    return render(request, "messengers/view_media.html", context)
