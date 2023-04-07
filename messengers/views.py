from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Messages, User, Friends
from .form import NewMessage

# Create your views here.


def index(request):
    return render(request, "messengers/index.html")


# def profile(request, user_id):
#     user_p = User.objects.get(id=user_id)
#     context = {"user_p": user_p}
#     return render(request, "messengers/profile.html", context)


def user_bio(request, user_id):
    user_bio = User.objects.get(id=user_id)
    bio_friends = Friends.get_friends(Friends, user_bio)
    user_friends = Friends.get_friends(Friends, request.user)
    context = {"user_bio": user_bio, "bio_friends": bio_friends,
               "user_friends": user_friends}
    return render(request, "messengers/user_bio.html", context)

# check if users are friends


def users(request):
    users = User.objects.exclude(id=request.user.id)
    friends = Friends.get_friends(Friends, request.user)
    context = {"users": users, "friends": friends}
    return render(request, "messengers/users.html", context)


def messages(request):
    users = User.objects.exclude(id=request.user.id)
    friends = Friends.get_friends(Friends, request.user)
    context = {"users": users, "friends": friends}
    return render(request, "messengers/messages.html", context)


def view_messages(request, rec_id):
    rec_user = User.objects.get(id=rec_id)
    sent_msgs = Messages.objects.filter(
        sender=request.user, receiver=rec_user)
    rec_msgs = Messages.objects.filter(
        sender=rec_user, receiver=request.user)
    all_msgs = (sent_msgs | rec_msgs).order_by("date_added")
    if request.method != "POST":
        form = NewMessage()
    else:
        form = NewMessage(data=request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender, new_message.receiver = request.user, rec_user
            new_message.save()
            return redirect("messengers:view_messages", rec_id=rec_id)
    context = {"all_messages": all_msgs, "form": form,
               "rec_id": rec_id, "rec_user": rec_user}
    return render(request, "messengers/view_messages.html", context)


def send_request(request, rec_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if sender not in Friends.requests(Friends):
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
    return users(request)


def send_request_bio(request, rec_id, bio_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    if sender not in Friends.requests(Friends):
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
    return user_bio(request, bio_id)


def cancel_request_bio(request, rec_id, bio_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    Friends.objects.get(req_sender=sender, req_receiver=receiver).delete()
    return user_bio(request, bio_id)


def cancel_request(request, rec_id):
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    Friends.objects.get(req_sender=sender, req_receiver=receiver).delete()
    return users(request)


def friend_requests(request):
    fr_requests = Friends.objects.filter(
        req_receiver=request.user, status=False)
    context = {"fr_requests": fr_requests}
    return render(request, "messengers/friend_requests.html", context)


def accept_request(request, sen_id):
    sender = User.objects.get(id=sen_id)
    receiver = request.user
    accepted = Friends.objects.get(req_sender=sender, req_receiver=receiver)
    accepted.status = True
    accepted.sent_status = False
    accepted.save()
    fr_requests = Friends.objects.filter(req_receiver=receiver, status=False)
    context = {"fr_requests": fr_requests}
    return render(request, "messengers/friend_requests.html", context)


def friends(request, user_id):
    user = User.objects.get(id=user_id)
    friends = Friends.get_friends(Friends, user)
    context = {"friends": friends}
    return render(request, "messengers/friends.html", context)
