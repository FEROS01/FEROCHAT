from django import template
from messengers.models import Friends
from messengers.models import Messages

register = template.Library()


@register.filter(name="la_st")
def last_message(val, arg):
    if arg.__class__.__name__ == "User":
        sent = val.sender.filter(receiver=arg)
        rec = val.receiver.filter(sender=arg)
        all = (sent | rec).order_by("date_sent")
    else:
        all = arg.grp_receiver.all()
    li = []
    for al in all:
        if al.media and not al.text:
            li.append([al.media_type(), al.date_sent])
        else:
            li.append([al.text, al.date_sent])
    return li if li else [""]


@register.filter()
def unread(val, arg):
    if arg.__class__.__name__ == "User":
        rec_msgs = Messages.objects.filter(sender=arg, receiver=val)
        no_unread = rec_msgs.filter(read=False).count()
        return no_unread
    else:
        grp_rec_msgs = Messages.objects.filter(grp_receiver=arg)
        no_unread = grp_rec_msgs.exclude(
            read_by__username=val.username).count()
        return no_unread


@register.filter(name="chec_k")
def if_sent(val, arg):
    try:
        return Friends.objects.filter(req_sender=val, req_receiver=arg)[0].sent_status
    except:
        return False


@register.filter(name="m_type")
def m_type(val):
    return val.media_type()


@register.filter(name="nam_e")
def name(val):
    return val.split("/")[3].split(".")


@register.filter(name="check_instance")
def check_instance(val):
    return val.__class__.__name__ == "User"
