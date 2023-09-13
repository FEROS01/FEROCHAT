from functools import wraps

from django.shortcuts import render, redirect
from django.db.models import Q

from Groups.models import Group, Membership

from .models import User, Friends


def confirm_type(function):
    """Decorator that checks if its a user or a group"""
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        _type = kwargs.get("_type")
        if _type == "User" or _type == "Group":
            return function(request, *args, **kwargs)
        context = {"error": f"The path '{request.path}' is invalid"}
        return render(request, "messengers/page_error.html", context)
    return wrapper


def confirm_member_friend(function):
    """Decorator that checks for valid receiver or group"""
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        _type = kwargs.get("_type")
        rec_id = kwargs.get("rec_id")
        group_exists = Group.objects.filter(id=rec_id).exists()
        receiver_exists = User.objects.filter(id=rec_id).exists()
        context = {"error": f"The path '{request.path}' is invalid"}
        if _type == "User" and receiver_exists:
            receiver = User.objects.get(id=rec_id)
            friendship_exists = Friends.objects.filter(
                Q(req_sender=request.user, req_receiver=receiver) |
                Q(req_sender=receiver, req_receiver=request.user),
                status=True
            ).exists()
            if friendship_exists:
                return function(request, *args, **kwargs)
            context = {
                "error": "Sorry you cannot message this user because you are not friends"}
        elif _type == "Group" and group_exists:
            group = Group.objects.get(id=rec_id)
            membership_exists = Membership.objects.filter(
                group=group, member=request.user).exists()
            if membership_exists:
                return function(request, *args, **kwargs)
            context = {
                "error": "Sorry you cannot message this group because you are not a member"}
        elif _type == None and receiver_exists:
            receiver = User.objects.get(id=rec_id)
            friendship_exists = Friends.objects.filter(
                Q(req_sender=request.user, req_receiver=receiver) |
                Q(req_sender=receiver, req_receiver=request.user),
                status=True
            ).exists()
            if friendship_exists:
                return function(request, *args, **kwargs)
            context = {
                "error": "Sorry you cannot message this user because you are not friends"}
        return render(request, 'messengers/page_error.html', context)
    return wrapper
