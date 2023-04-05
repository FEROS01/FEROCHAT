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
    context = {"user_bio": user_bio}
    return render(request, "messengers/user_bio.html", context)


def users(request):
    users = User.objects.all()
    context = {"users": users}
    return render(request, "messengers/users.html", context)


def messages(request):
    users = User.objects.all()
    context = {"users": users}
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
# add notification for friend request


def send_request(request, rec_id):
    users = User.objects.all()
    # new_friend = Friends()
    sender = request.user
    receiver = User.objects.get(id=rec_id)
    # new_friend.save()
    Friends.objects.create(
        req_sender=sender, req_receiver=receiver, sent_status=True)
    context = {"users": users}
    return render(request, "messengers/users.html", context)


def friend_requests(request):
    fr_requests = Friends.objects.filter(req_receiver=request.user)
    context = {"fr_requests": fr_requests}
    return render(request, "messengers/friend_requests.html", context)
