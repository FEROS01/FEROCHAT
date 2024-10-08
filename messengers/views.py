from datetime import datetime
import pytz


from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.contrib.auth.models import User
from django.contrib import messages as Msg
from django.utils import timezone as tz
from django.http import HttpResponse, Http404
from django_htmx.middleware import HtmxDetails
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods, require_POST

from messenger.utils import _find_users
from Groups.models import Group

from .models import Messages, Friends, Info
from .form import NewMessage, Search, SearchMessages
from .utils import _send_message, _update_unread_messages, _assign_type_variables
from .decorators import confirm_type, confirm_member_friend, confirm_htmx_request

timezone = tz.get_current_timezone()


class HtmxHttpResponse(HttpResponse):
    htmx: HtmxDetails


def set_timezone(request):
    django_timezone_exist = request.session.get('django_timezone',False)
    if request.method == "POST" and not django_timezone_exist:
        request.session["django_timezone"] = request.POST["timezone"]
    return HttpResponse('')

def index(request):
    return render(request, "messengers/index.html")


@login_required
def user_bio(request, user_id):
    user_bio = get_object_or_404(User, id=user_id)
    user_friends = Friends.get_friends(Friends, request.user)
    bio_friends = Friends.get_friends(
        Friends, user_bio, exclude=request.user)
    mutual_friends = bio_friends.intersection(user_friends)
    other_friends = bio_friends.difference(user_friends)
    context = {
        "user_bio": user_bio, "bio_friends": bio_friends,
        "user_friends": user_friends, "mutual_friends": mutual_friends, "other_friends": other_friends
    }
    return render(request, "messengers/user_bio.html", context)


@login_required
def users(request: HtmxHttpResponse):
    users = User.objects.exclude(
        username='FeroChat').order_by(Lower('username'))
    friends = Friends.get_friends(Friends, request.user)
    searched = False
    if request.htmx and request.method == 'POST':
        form = Search(data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            search = data["search"].lower()
            users = _find_users(users, search)
        context = {"users": users, "friends": friends,
                   "form": form, "search": data['search']}
        return render(request, "htmx_templates/people_search.html", context)
    elif request.method != "POST":
        form = Search()
    context = {"users": users, "friends": friends,
               "form": form, "searched": searched}
    return render(request, "messengers/users.html", context)


@login_required
def messages(request):
    friends = Friends.get_m_friends(Friends, request.user)
    searched = False
    msgs = Messages.objects.none()

    if request.method != "POST":
        form = SearchMessages()
    else:

        form = SearchMessages(data=request.POST)
        if form.is_valid():
            searched = True
            data = form.cleaned_data["search"]
            groups = request.user.members.all()
            msgs = Messages.objects.filter(
                Q(receiver=request.user) |
                Q(sender=request.user)
            )
            group_msgs = Messages.objects.filter(grp_receiver__in=groups)
            group_msgs = group_msgs.exclude(sender=request.user)
            msgs = (msgs | group_msgs).order_by("-date_sent")
            msgs = msgs.filter(text__contains=data)
    context = {"friends": friends, "form": form,
               "message_s": msgs, "searched": searched}
    return render(request, "messengers/messages.html", context)


@login_required
def message_search(request):
    if request.method == "GET":
        search_string = request.GET['search']
        friends = Friends.get_friends(Friends,request.user)
        groups = request.user.members.all()
        msgs = Messages.objects.filter(
            Q(receiver=request.user)|Q(sender=request.user),
            Q(sender__in=friends)|Q(receiver__in=friends)
        )
        group_msgs = Messages.objects.filter(grp_receiver__in=groups)
        group_msgs = group_msgs.exclude(sender=request.user)
        msgs = (msgs | group_msgs).order_by("-date_sent")
        msgs = msgs.filter(text__contains=search_string)
        context = {"message_s": msgs}
        return render(request, "htmx_templates/message_search_result.html", context)
    else:
        return HttpResponse('<div class="message_list">failed</div>')


@login_required
@confirm_type
@confirm_member_friend
def view_messages(request:HtmxHttpResponse, rec_id, _type):

    # This is the app's administrator that sends messages to new users and shares updates to all users
    ferochat = User.objects.get(username='FeroChat')
    is_dark = request.user.info.dark_theme
    theme = 'dark' if is_dark else 'light'
    unread_id = None
    old_errors = []
    room_name,rec_msgs, rec_user, all_msgs, grp_members = _assign_type_variables(
        request, _type, rec_id)
    is_ferochat = rec_user == ferochat

    if request.method != "POST":
        unread_id = _update_unread_messages(
            request, rec_msgs, all_msgs, _type)
        form = NewMessage()
        search_form = SearchMessages()
    elif request.method == "POST" and request.htmx:
        messages = []
        files = request.FILES.getlist('media')
        search_form = SearchMessages()
        form = NewMessage(request.POST, request.FILES)
        if is_ferochat:
            Msg.error(request, 'You cannot message FEROCHAT')
        elif 'method' in request.POST:
            messages_copy = all_msgs.exclude(
            Q(read_by__id=request.user.id)|
            Q(read=True)
            )
            messages = list(messages_copy)
            unread_id = _update_unread_messages(
            request, messages_copy, all_msgs, _type)
            unread_id = None
        elif not files or len(files) == 1:
            if form.is_valid():
                message = _send_message(request, form, rec_user, _type)
                messages.append(message)
            else:
                old_errors.append(form.errors["media"])
        else:
            for file in files:
                request.FILES["media"] = file
                form = NewMessage(request.POST, request.FILES)
                if form.is_valid():
                    message = _send_message(request, form, rec_user, _type)
                    messages.append(message)
                else:
                    if form.errors["media"] not in old_errors:
                        old_errors.append(form.errors["media"])
        context = {
        "all_messages": messages, "rec_id": rec_id, "rec_user": rec_user,
        "unread_id": unread_id, "old_errors": old_errors, "members": grp_members, "is_ferochat": is_ferochat,"type": _type
        }
        return render(request, "htmx_templates/message.html", context)
    context = {
        "all_messages": all_msgs, "form": form, "search_form": search_form, "rec_id": rec_id, "rec_user": rec_user,
        "unread_id": unread_id, "old_errors": old_errors, "type": _type, "members": grp_members, "is_ferochat": is_ferochat, "room_name":room_name,"theme":theme
    }
    return render(request, "messengers/view_messages.html", context)


@login_required
def send_request(request, rec_id):
    receiver = get_object_or_404(User, id=rec_id)
    sender = request.user
    check_request = Friends.check_request(Friends, sender, receiver)
    if sender != receiver and not check_request:
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
        Msg.success(request, "Friend request sent!")
        request.user.info.notifications += 1
        receiver.info.notifications += 1
        receiver.info.save()
        request.user.info.save()
    else:
        Msg.error(request, "Friend request was not sent!")
    return users(request)


@login_required
def send_request_bio(request, rec_id, bio_id):
    receiver = get_object_or_404(User, id=rec_id)
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
    return user_bio(request, user_id=bio_id)


@login_required
def cancel_request_bio(request, rec_id, bio_id):
    receiver = get_object_or_404(User, id=rec_id)
    sender = request.user
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.filter(req_sender=sender, req_receiver=receiver,
                               sent_status=True).update(sent_status=False, friend_date=datetime.now(tz=timezone))
        Msg.success(request, "Friend request canceled!")
        sender.info.notifications += 1
        receiver.info.notifications += 1
        receiver.info.save()
        sender.info.save()
    return user_bio(request, user_id=bio_id)


@login_required
def cancel_request(request, rec_id):
    receiver = get_object_or_404(User, id=rec_id)
    sender = request.user
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.filter(req_sender=sender, req_receiver=receiver,
                               sent_status=True).update(sent_status=False, friend_date=datetime.now(tz=timezone))
        Msg.success(request, "Friend request canceled!")
        sender.info.notifications += 1
        receiver.info.notifications += 1
        receiver.info.save()
        sender.info.save()
    return users(request=request)


@login_required
def notifications(request):
    ferochat = User.objects.get(username='FeroChat')
    fr_requests = Friends.objects.filter(
        Q(req_receiver=request.user) |
        Q(req_sender=request.user)
    ).exclude(req_sender=ferochat).order_by("-friend_date")
    request.user.info.notifications = 0
    request.user.info.save()
    context = {"fr_requests": fr_requests}
    return render(request, "messengers/notifications.html", context)


@login_required
def accept_request(request, sen_id):
    sender = User.objects.filter(id=sen_id)
    if sender.exists():
        sender = sender.first()
        receiver = request.user
        accepted = Friends.objects.filter(
            req_sender=sender, req_receiver=receiver, sent_status=True)
        if accepted.exists():
            accepted.update(status=True, sent_status=False,
                            friend_date=datetime.now(tz=timezone))
            sender.info.notifications += 1
            sender.info.save()
            Msg.success(request, "Friend request accepted!")
            return notifications(request=request)
    Msg.error(request, "Cannot accept request")
    return notifications(request=request)


@login_required
def decline_request(request, sen_id):
    sender = get_object_or_404(User, id=sen_id)
    receiver = request.user
    if Friends.check_request(Friends, sender, receiver):
        Friends.objects.filter(req_sender=sender, req_receiver=receiver, sent_status=True).update(
            sent_status=False, rejected=True, friend_date=datetime.now(tz=timezone))
        Msg.success(request, "Friend request declined!")
        sender.info.notifications += 1
        sender.info.save()
    return notifications(request=request)


@login_required
def friends(request: HtmxHttpResponse, user_id):
    user = get_object_or_404(User, id=user_id)
    friends = Friends.get_friends(Friends, user).exclude(
        username='FeroChat').order_by("username")
    searched = False
    if request.method != "POST":
        form = Search()
    elif request.htmx and request.method == 'POST':
        form = Search(data=request.POST)
        search = ''
        if form.is_valid():
            data = form.cleaned_data
            search = data["search"].lower()
            friends = _find_users(friends, search).order_by("username")
            searched = True
        context = {"friends": friends, "search": search}
        return render(request, "htmx_templates/friends_search.html", context)
    context = {"friends": friends, "searched": searched, "form": form}
    return render(request, "messengers/friends.html", context)


@login_required
def unfriend(request, user_id, friend_id):
    ferochat = User.objects.get(username='FeroChat')
    friend = get_object_or_404(User, id=friend_id)
    if friend != ferochat:
        Friends.objects.filter(
            Q(req_sender=friend, req_receiver=request.user, status=True) |
            Q(req_sender=request.user, req_receiver=friend, status=True)
        ).delete()
        Msg.error(request, f"You have unfriend {friend}")
        return friends(request=request, user_id=user_id)
    Msg.error(request, "Cannot unfriend this user")
    return friends(request=request, user_id=user_id)


@login_required
@confirm_type
@confirm_member_friend
def view_media(request, rec_id, _type):
    receiver = get_object_or_404(User, id=rec_id)
    messages = Messages.objects.filter(
        Q(sender=request.user, receiver=receiver) |
        Q(sender=receiver, receiver=request.user)
    ).order_by("-date_sent")
    media_msgs = messages.exclude(
        Q(media__isnull=True) | Q(media__exact=""))
    context = {"media_mesgs": media_msgs, "rec_id": rec_id}
    return render(request, "messengers/view_media.html", context)


@login_required
@confirm_htmx_request
@confirm_member_friend
@confirm_type
@require_http_methods(["DELETE"])
def delete_message(request, msg_id, rec_id, _type):
    message = get_object_or_404(Messages, id=msg_id)
    delete_allowed = message.sender == request.user
    if delete_allowed:
        if _type == "User":
            rec_user = get_object_or_404(User, id=rec_id)
            if not message.read:
                rec_user.info.unread_messages -= 1
                rec_user.info.save()
        elif _type == "Group":
            group = Group.objects.get(id=rec_id)
            message = get_object_or_404(Messages, id=msg_id)
            members = group.members.exclude(id=request.user.id)
            members_read = message.read_by.all()
            members_unread_id = members.difference(
                members_read).values_list('id', flat=True)
            Info.objects.filter(user__id__in=members_unread_id).update(
                unread_messages=F("unread_messages")-1)
        message.delete()
        return HttpResponse('')
    raise Http404('Cannot delete message')


@login_required
@require_POST
@confirm_member_friend
@confirm_type
def search_result(request, rec_id, _type):
    room_name,rec_msgs, rec_user, all_msgs, grp_members = _assign_type_variables(
        request, _type, rec_id)
    search_mesg = request.POST.get("search", "")
    result = all_msgs.filter(text__contains=search_mesg).order_by('-date_sent')
    context = {"result": result, "rec_id": rec_id, "type": _type}

    # Returns results if there was searched text
    return render(request, "htmx_templates/search_result.html", context) if search_mesg else HttpResponse('')


@login_required
@confirm_htmx_request
def blank(request):
    return HttpResponse('')


@login_required
@confirm_htmx_request
@require_POST
def media_name(request):
    # form = NewMessage(files=request.FILES)
    # errors = form.errors
    files = []
    for file in request.FILES.getlist('media'):
        request.FILES['media'] = file
        form = NewMessage(files=request.FILES)
        file_object = {"name": file.name,
                       "size": file.size,
                       "error": form.errors.get('media', '')
                       }
        files.append(file_object)
    # files = [{"name": file.name, "size": file.size}
    #          for file in request.FILES.getlist('media')]
    return render(request, "htmx_templates/media_name.html", {"files": files})
