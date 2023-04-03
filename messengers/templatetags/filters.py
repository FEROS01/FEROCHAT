from django import template
# from messengers.models import User,Messages

register = template.Library()


@register.filter(name="la_st")
def last_message(val, arg):
    # return "fish"
    sent = val.sender.filter(receiver=arg)
    rec = val.receiver.filter(sender=arg)
    all = (sent | rec).order_by("date_added")
    li = [al.text for al in all]
    return li if li else [""]
