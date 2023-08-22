from datetime import datetime, timedelta
import pytz

from django.shortcuts import render, redirect

from messengers.form import Search
from messengers.models import Group, User, Membership, Friends
from messengers.views import user_bio
from messenger.settings import TIME_ZONE

from .forms import GroupEditForm, SelectMemberForm, GroupCreationForm


timezone = pytz.timezone(TIME_ZONE)
# Create your views here.


def _group_setup(request, data):
    group = Group.objects.create(
        name=data["name"],
        creator=request.user,
        description=data["description"],
        prof_pics=data["prof_pics"],
    )
    group.members.set(
        data["members"], through_defaults={
            "inviter": request.user,
            "date_joined": datetime.now(tz=timezone)
        }
    )

    group.members.add(
        request.user, through_defaults={
            "inviter": request.user,
            "date_joined": datetime.now(tz=timezone)-timedelta(minutes=1)
        }
    )
    group.admins.add(request.user)
    return redirect("messengers:user_bio", user_id=group.id, _type="Group")


def create_group(request):
    users = User.objects.all().exclude(id=request.user.id)
    searched = False
    if request.method != "POST":
        form = GroupCreationForm()
        search_form = Search()
    elif request.method == "POST" and "create" in request.POST:
        search_form = Search()
        form = GroupCreationForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            return _group_setup(request, data)
    elif request.method == "POST" and "search" in request.POST:
        searched = True
        search_form = Search(request.POST)
        form = GroupCreationForm()
    context = {"form": form, "users": users, "search_form": search_form}
    return render(request, "Groups/create_group.html", context)


def edit_group(request, grp_id):
    group = Group.objects.get(id=grp_id)
    if request.method != 'POST':
        form = GroupEditForm(instance=group)
    else:
        form = GroupEditForm(request.POST, request.FILES, instance=group)
        print(form.errors)
        print(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("messengers:user_bio", user_id=grp_id, _type="Group")
    context = {"form": form, "grp_id": grp_id, "group": group}
    return render(request, "Groups/edit_group.html", context)


def remove_user(request, user_id, grp_id):
    group = Group.objects.get(id=grp_id)
    creator = group.creator
    user = User.objects.get(id=user_id)
    membership = Membership.objects.filter(group=group, member=user)
    admin = group.admins.filter(id=user.id)
    if membership and user != creator:
        membership.delete()
        if admin.exists():
            group.admins.remove(admin.first())
    return user_bio(request, grp_id, "Group")


def _search_members(users, data):
    lis = []
    for user in users:
        search = data["search"].lower()
        name = [
            user.username.lower().startswith(search),
            user.last_name.lower().startswith(search),
            user.first_name.lower().startswith(search)
        ]
        if any(name):
            lis.append(user)
    return lis


def select_member(request, grp_id):
    all = User.objects.all()
    group = Group.objects.get(id=grp_id)
    members = group.members.all()
    users = all.difference(members)
    friends = Friends.get_friends(Friends, request.user, exclude=request.user)
    searched = False
    form1 = SelectMemberForm(selected_choices=[])
    if request.method != "POST":
        form = Search()
    elif request.method == "POST" and "search" in request.POST:
        form = Search(request.POST)
        if form.is_valid():
            searched = True
            data = form.cleaned_data
            users = _search_members(users, data)
    elif request.method == "POST" and "slct_mbrs" in request.POST:
        CHOICES = [(user.username, user.username) for user in users]
        form = Search()
        form1 = SelectMemberForm(data=request.POST, selected_choices=CHOICES)
        if form1.is_valid():
            members = form1.cleaned_data["users"]
            for user in members:
                member = User.objects.get(username=user)
                Membership.objects.create(
                    group=group, member=member, inviter=request.user)
            return redirect("messengers:user_bio", user_id=grp_id, _type="Group")
    context = {"users": users, "friends": friends,
               "form": form, "searched": searched, "grp_id": grp_id, "form1": form1}
    return render(request, "Groups/select_member.html", context)
