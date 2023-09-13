from functools import wraps

from django.shortcuts import render, redirect


from .models import Group


def group_exists(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        grp_id = kwargs.get("grp_id")
        group = Group.objects.filter(id=grp_id)
        if group.exists():
            return function(request, *args, **kwargs)
        context = {"error": "Group does not exist"}
        return render(request, "messengers/page_error.html", context)
    return wrapper


def is_admin(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        grp_id = kwargs.get("grp_id")
        group = Group.objects.filter(id=grp_id)
        is_admin = request.user in group.first().admins.all() if group.exists() else False
        if is_admin:
            return function(request, *args, **kwargs)
        context = {"error": "You are not an admin"}
        return render(request, "messengers/page_error.html", context)
    return wrapper
