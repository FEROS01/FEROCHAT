from functools import wraps

from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from Groups.models import Group, Membership

from .models import User, Friends


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails


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
    """Decorator that checks if user is a friend or member of group """
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        _type, rec_id = kwargs.get("_type"), kwargs.get("rec_id")
        if _type == "User":
            receiver = get_object_or_404(User, id=rec_id)
            friendship = get_object_or_404(
                Friends,
                Q(req_sender=request.user, req_receiver=receiver) |
                Q(req_sender=receiver, req_receiver=request.user),
                status=True
            )
            return function(request, *args, **kwargs)
        else:
            group = get_object_or_404(Group, id=rec_id)
            membership = get_object_or_404(
                Membership,
                group=group,
                member=request.user
            )
            return function(request, *args, **kwargs)
    return wrapper


def confirm_htmx_request(function):
    """Decorator that checks if function's request is an htmx request"""
    @wraps(function)
    def wrapper(request: HtmxHttpRequest, *args, **kwargs):
        if request.htmx:
            return function(request, *args, **kwargs)
        else:
            context = {
                "error": "You cannot access this page"}
            return render(request, 'messengers/page_error.html', context)
    return wrapper
