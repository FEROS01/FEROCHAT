from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat


def _find_users(users, search):
    users = users.annotate(
        full_name=Concat('first_name', Value(
            " "), 'last_name', output_field=CharField()),
        full_name_r=Concat('last_name', Value(
            " "), 'first_name', output_field=CharField())
    ).filter(
        Q(username__startswith=search) |
        Q(first_name__startswith=search) |
        Q(last_name__startswith=search) |
        Q(full_name__contains=search) |
        Q(full_name_r__contains=search)
    )
    return users
