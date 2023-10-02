from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages as Msg


from .models import Group, Membership, User


def _group_setup(request, data):
    group = Group.objects.create(
        name=data["name"],
        creator=request.user,
        description=data["description"],
        prof_pics=data["prof_pics"],
    )
    group.members.set(
        data["members"], through_defaults={"inviter": request.user}
    )

    group.members.add(
        request.user, through_defaults={"inviter": request.user}
    )
    group.admins.add(request.user)
    Msg.success(request, 'Group ceation is succesful')
    return redirect("Groups:group_bio", grp_id=group.id)


def _search_members(users, non_admin_members, data):
    search = data["search"]
    users = users.filter(
        Q(username__startswith=search) |
        Q(last_name__startswith=search) |
        Q(first_name__startswith=search)
    )
    non_admin_members = non_admin_members.filter(
        Q(username__startswith=search) |
        Q(last_name__startswith=search) |
        Q(first_name__startswith=search)
    )
    return users, non_admin_members


def _add_members(request, form1, group, grp_id):
    selected_members = form1.cleaned_data["users"]
    selected_admins = form1.cleaned_data["admins"]

    for user in selected_members:
        user = User.objects.get(username=user)
        Membership.objects.create(
            group=group, member=user, inviter=request.user)

    for member in selected_admins:
        member = User.objects.get(username=member)
        group.admins.add(member)
    Msg.success(request, 'Members and admins added succesfully')
    return redirect("Groups:group_bio", grp_id=grp_id)
