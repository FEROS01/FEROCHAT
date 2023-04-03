from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Messages, User
from .form import NewMessage

# Create your views here.


def index(request):
    return render(request, "messengers/index.html")

def user_bio(request,user_id):
    users = User.objects.get(id=user_id)
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
               "rec_id": rec_id}
    return render(request, "messengers/view_messages.html", context)
