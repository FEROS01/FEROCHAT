from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages as Msg
from .models import Messages, User, Friends
from .form import NewMessage, Search, SearchMessages
from datetime import datetime

# Create your views here.


def index(request):
    return render(request, "messengers/index.html")


def user_bio(request, user_id):
    user_bio = User.objects.get(id=user_id)
    bio_friends = Friends.get_friends(Friends, user_bio, exclude=request.user)
    user_friends = Friends.get_friends(Friends, request.user)
    context = {"user_bio": user_bio, "bio_friends": bio_friends,
               "user_friends": user_friends}
    return render(request, "messengers/user_bio.html", context)


def users(request):
    users = User.objects.exclude(id=request.user.id)
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
    msgs = msgs.order_by("-date_added")
    if request.method != "POST":
        form = SearchMessages()
    else:
        form = SearchMessages(data=request.POST)
        if form.is_valid():
            searched = True
            data = form.cleaned_data["search"].lower()
            msgs = _search(data, msgs)
    context = {"friends": friends, "form": form,
               "message_s": msgs, "searched": searched}
    return render(request, "messengers/messages.html", context)


def view_messages(request, rec_id):
    searched = True
    rec_user = User.objects.get(id=rec_id)
    sent_msgs = Messages.objects.filter(
        sender=request.user, receiver=rec_user)
    rec_msgs = Messages.objects.filter(
        sender=rec_user, receiver=request.user)
    all_msgs = (sent_msgs | rec_msgs).order_by("date_added")
    count = 0
    unread_id = None
    if request.method != "POST":
        no_unread_msgs = rec_msgs.filter(read=False).count()
        request.user.info.unread_messages -= no_unread_msgs
        request.user.info.save()
        for msg in rec_msgs:
            if msg.read == False and count == 0:
                count += 1
                unread_id = msg.id
        rec_msgs.update(read=True)
        for mesg in rec_msgs:
            mesg.save()
        searched = False
        form = NewMessage()
        search_form = SearchMessages()
    elif "next" in request.POST:
        form = NewMessage(request.POST, request.FILES)
        search_form = SearchMessages()
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender, new_message.receiver = request.user, rec_user
            new_message.read = False
            rec_user.info.unread_messages += 1
            rec_user.info.save()
            new_message.save()
            return redirect("messengers:view_messages", rec_id=rec_id)
    else:
        form = NewMessage()
        search_form = SearchMessages(request.POST)
        if search_form.is_valid():
            search_mesg = search_form.cleaned_data["search"].lower()
            all_msgs = _search(search_mesg, all_msgs)
    context = {
        "all_messages": all_msgs, "form": form, "search_form": search_form, "searched": searched, "rec_id": rec_id, "rec_user": rec_user,
        "unread_id": unread_id,
    }
    return render(request, "messengers/view_messages.html", context)


def delete_message(request, msg_id, rec_id):
    try:
        Messages.objects.get(id=msg_id).delete()
        return view_messages(request, rec_id)
    except:
        return view_messages(request, rec_id)


def send_request(request, rec_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if not Friends.check_request(Friends, sender, receiver):
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
        Msg.success(request, "Friend request sent!")
    return users(request)


def send_request_bio(request, rec_id, bio_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if not Friends.check_request(Friends, sender, receiver):
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
        Msg.success(request, "Friend request sent!")
    return user_bio(request, bio_id)


def cancel_request_bio(request, rec_id, bio_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.get(req_sender=sender, req_receiver=receiver).delete()
        Msg.success(request, "Friend request canceled!")
    return user_bio(request, bio_id)


def cancel_request(request, rec_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.get(req_sender=sender, req_receiver=receiver).delete()
        Msg.success(request, "Friend request canceled!")
    return users(request)


def notifications(request):
    fr_requests = Friends.objects.filter(
        req_receiver=request.user, status=False)
    context = {"fr_requests": fr_requests}
    return render(request, "messengers/notifications.html", context)


def accept_request(request, sen_id):
    sender = User.objects.get(id=sen_id)
    receiver = request.user
    accepted = Friends.objects.get(req_sender=sender, req_receiver=receiver)
    accepted.status = True
    accepted.sent_status = False
    accepted.save()
    Msg.success(request, "Friend request accepted!")
    return notifications(request)


def decline_request(request, sen_id):
    sender = User.objects.get(id=sen_id)
    receiver = request.user
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.get(req_sender=sender, req_receiver=receiver).delete()
        Msg.success(request, "Friend request declined!")
    return notifications(request)


def friends(request, user_id):
    user = User.objects.get(id=user_id)
    friends = Friends.get_friends(Friends, user)
    c_friends = friends[0:]
    searched = False
    if request.method != "POST":
        form = Search()
    else:
        form = Search(data=request.POST)
        if form.is_valid():
            searched = True
            data = form.cleaned_data
            for friend in c_friends:
                search = data["search"].lower()
                name = [friend.username.lower().startswith(search), friend.last_name.lower(
                ).startswith(search), friend.first_name.lower().startswith(search)]
                if not any(name):
                    friends.remove(friend)
    context = {"friends": friends, "searched": searched, "form": form}
    return render(request, "messengers/friends.html", context)


def unfriend(request, user_id, friend_id):
    friend = User.objects.get(id=friend_id)
    try:
        Friends.objects.get(
            req_sender=friend, req_receiver=request.user).delete()
    except:
        Friends.objects.get(
            req_sender=request.user, req_receiver=friend).delete()
    return friends(request, user_id)
