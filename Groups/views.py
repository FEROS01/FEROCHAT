from datetime import datetime
import pytz

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Case, Value, When
from django_htmx.middleware import HtmxDetails
from django.contrib.auth.models import User
from django.contrib import messages as Msg
from django.http import HttpRequest


from messengers.form import Search
from messengers.models import Friends
from messenger.settings import TIME_ZONE
from messenger.utils import _find_users

from .models import Group, Membership
from .forms import GroupEditForm, SelectMemberForm, GroupCreationForm
from .utils import _group_setup, _add_members
from .decorators import is_admin
timezone = pytz.timezone(TIME_ZONE)


class HtmxHttpResponse(HttpRequest):
    htmx: HtmxDetails


@login_required
def create_group(request: HtmxHttpResponse):
    ferochat = User.objects.get(username='FeroChat')
    friends = Friends.get_friends(Friends,request.user,exclude=ferochat)
    searched = False
    if request.method != "POST":
        form = GroupCreationForm()
        search_form = Search()
    elif request.htmx and request.method == 'POST':
        search_form = Search(request.POST)
        form = GroupCreationForm()
        if search_form.is_valid():
            search = search_form.cleaned_data["search"]
            friends = _find_users(friends, search)
        context = {"form": form, "users": friends,
                   "search_form": search_form, "searched": searched}
        return render(request, "htmx_templates/create_group_result.html", context)

    elif request.method == "POST" and "create" in request.POST:
        search_form = Search()
        form = GroupCreationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            return _group_setup(request, data)
    context = {"form": form, "users": friends,
               "search_form": search_form, "searched": searched}
    return render(request, "Groups/create_group.html", context)


@login_required
@is_admin
def edit_group(request, grp_id):
    group = get_object_or_404(Group, id=grp_id)
    if request.method != 'POST':
        form = GroupEditForm(instance=group)
    else:
        form = GroupEditForm(request.POST, request.FILES, instance=group)
        if form.is_valid():
            form.save()
            Msg.success(
                request, "Group's Profile has been successfully updated")
            return redirect("Groups:group_bio", grp_id=grp_id)
    context = {"form": form, "grp_id": grp_id, "group": group}
    return render(request, "Groups/edit_group.html", context)


@login_required
@is_admin
def remove_user(request, user_id, grp_id):
    user = get_object_or_404(User, id=user_id)
    group = get_object_or_404(Group, id=grp_id)
    creator = group.creator
    membership = get_object_or_404(Membership, group=group, member=user)
    admin = group.admins.filter(id=user.id)
    if user != creator:
        no_unread_messages = group.grp_receiver.exclude(read_by=user).count()
        user.info.unread_messages -= no_unread_messages
        user.info.save()
        membership.delete()
        Msg.success(request, f"{user.username} has been removed from group")
        if admin.contains(user):
            group.admins.remove(admin.first())
    return redirect("Groups:group_bio", grp_id=grp_id)


@login_required
@is_admin
def select_member(request: HtmxHttpResponse, grp_id):
    all = Friends.get_friends(Friends,request.user).exclude(username='FeroChat')
    group = get_object_or_404(Group, id=grp_id)
    admins = group.admins.all()
    admins_id = admins.values_list("id", flat=True)
    members = group.members.all()
    members_id = members.values_list("id", flat=True)
    users = all.exclude(id__in=members_id)
    non_admin_members = members.exclude(id__in=admins_id)
    friends = Friends.get_friends(Friends, request.user, exclude=request.user)
    searched = False
    form1 = SelectMemberForm(selected_choices=[], selected_admin_choices=[])
    if request.htmx and request.method == 'POST':
        form = Search(request.POST)
        if form.is_valid():
            searched = True
            data = form.cleaned_data['search']
            users = _find_users(users, data)
            non_admin_members = _find_users(non_admin_members, data)
        context = {"users": users, "friends": friends, "searched": searched,
                   "grp_id": grp_id, "form1": form1, "members": non_admin_members}
        return render(request, "htmx_templates/grp_search_result.html", context)
    elif request.method != "POST":
        form = Search()

    elif request.method == "POST" and "slct_mbrs" in request.POST:
        CHOICES = [(user.username, user.username) for user in users]
        ADMIN_CHOICES = [(user.username, user.username)
                         for user in non_admin_members]
        form = Search()
        form1 = SelectMemberForm(
            data=request.POST,
            selected_choices=CHOICES,
            selected_admin_choices=ADMIN_CHOICES
        )
        if form1.is_valid():
            return _add_members(request, form1, group, grp_id)
    context = {"users": users, "friends": friends,
               "form": form, "searched": searched, "grp_id": grp_id, "form1": form1, "members": non_admin_members}
    return render(request, "Groups/select_member.html", context)


@login_required
def remove_admin(request, admin_id, grp_id):
    group = get_object_or_404(Group, id=grp_id)
    admin = get_object_or_404(User, id=admin_id)
    is_creator = request.user == group.creator
    is_admin = group.admins.contains(admin)
    if is_admin and is_creator:
        group.admins.remove(admin)
        Msg.success(request, f"{admin.username} is now a member")
        return redirect("Groups:group_bio", grp_id=grp_id)
    Msg.error(request, "You cannot remove admins")
    return redirect("Groups:group_bio", grp_id=grp_id)


@login_required
def exit_group(request, grp_id):
    group = get_object_or_404(Group, id=grp_id)
    member = request.user

    if group.members.contains(member):
        user = request.user
        no_unread_messages = group.grp_receiver.exclude(read_by=user).count()
        user.info.unread_messages -= no_unread_messages
        user.info.save()
        group.members.remove(member)
        Msg.success(request, f"You have left {group.name}")
    if group.admins.contains(member):
        group.admins.remove(member)
    return redirect("messengers:messages")


@login_required
def group_bio(request, grp_id):
    group = get_object_or_404(Group, id=grp_id)
    user_friends = Friends.get_friends(Friends, request.user)
    user_friends_id = user_friends.values_list("id", flat=True)
    creator = group.creator
    all_members = group.members.all()
    no_members = all_members.count()
    admins_id = group.admins.values_list("id", flat=True)
    only_members = all_members.exclude(id__in=admins_id)
    admin_priority = Case(
        When(id=creator.id, then=Value(1)),
        When(id=request.user.id, then=Value(2)),
        default=Value(3)
    )
    member_priority = Case(
        When(id=request.user.id, then=Value(0)),
        When(id__in=user_friends_id, then=Value(1)),
        default=Value(2)
    )
    admins = group.admins.annotate(
        position=admin_priority).order_by("position", "username")
    members = only_members.annotate(
        position=member_priority).order_by("position", "username")
    context = {
        "group_bio": group, "members": members, "no_members": no_members, "admins": admins, "user_friends": user_friends, "creator": creator
    }
    return render(request, "Groups/group_bio.html", context)


@login_required
def send_request_bio(request, rec_id, bio_id):
    receiver = get_object_or_404(User, id=rec_id)
    sender = request.user
    check_request = Friends.check_request(Friends, sender, receiver)
    if sender != receiver and not check_request:
        Friends.objects.create(
            req_sender=sender, req_receiver=receiver, sent_status=True)
        Msg.success(request, "Friend request sent!")
        sender.info.notifications += 1
        receiver.info.notifications += 1
        receiver.info.save()
        sender.info.save()
    return redirect("Groups:group_bio", grp_id=bio_id)


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
    return redirect("Groups:group_bio", grp_id=bio_id)


@login_required
def view_media(request, grp_id):
    group = get_object_or_404(Group, id=grp_id)
    is_member = group.members.contains(request.user)
    if is_member:
        messages = group.grp_receiver.all()
        media_msgs = messages.exclude(
            Q(media__isnull=True) | Q(media__exact=""))
        context = {"media_mesgs": media_msgs, "rec_id": grp_id}
        return render(request, "Groups/view_media.html", context)
    context = {"error": "You are not a member"}
    return render(request, "messengers/page_error.html", context)
