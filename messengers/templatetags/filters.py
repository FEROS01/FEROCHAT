from django import template
from messengers.models import Friends
from messengers.models import Messages
from messengers.validators import Media

register = template.Library()


@register.filter(name="type")
def media_type(val):
    if val:
        extension = val.split(".")[-1]
        media_type = [typ_e for typ_e,
                      ext in Media.items() if extension in ext]
        return media_type[0]
    return ''


@register.filter()
def check_last(val, arg):
    date_join_group = val.membership_set.get(group=arg).date_joined
    all = arg.grp_receiver.filter(date_sent__gte=date_join_group)
    last_text = arg.last_text
    if last_text in all.values_list('text', flat=True):
        return last_text
    else:
        return ""

@register.filter()
def check_lastd(val, arg):
    date_join_group = val.membership_set.get(group=arg).date_joined
    all = arg.grp_receiver.filter(date_sent__gte=date_join_group)
    last_text = arg.last_text
    if last_text in all.values_list('text', flat=True):
        return arg.last_date
    else:
        return ""

@register.filter(name="la_st")
def last_message(val, arg):
    instance = arg.__class__.__name__
    if instance == "User":
        sent = val.sender.filter(receiver=arg)
        rec = val.receiver.filter(sender=arg)
        all = (sent | rec)
        if not all:
            return [""]
        else:
            last = all.latest("date_sent")
    else:
        date_join_group = val.membership_set.get(group=arg).date_joined
        all = arg.grp_receiver.filter(date_sent__gte=date_join_group)
        if not all:
            return [""]
        else:
            last = all.latest("date_sent")

    li = []
    if last.media and not last.text:
        if instance == "Group":
            li.append([f"{last.sender}: {last.media_type()}", last.date_sent])
        else:
            li.append([last.media_type(), last.date_sent])
    else:
        if instance == "Group":
            li.append([f"{last.sender}: {last.text}", last.date_sent])
        else:
            li.append([last.text, last.date_sent])
    return li


@register.filter()
def unread(val, arg):
    if arg.__class__.__name__ == "User":
        rec_msgs = Messages.objects.filter(sender=arg, receiver=val)
        no_unread = rec_msgs.filter(read=False).count()
        return no_unread
    else:
        date_join_group = val.membership_set.get(group=arg).date_joined
        grp_rec_msgs = Messages.objects.filter(
            grp_receiver=arg, date_sent__gte=date_join_group)
        no_unread = grp_rec_msgs.exclude(
            read_by__username=val.username).count()
        return no_unread


@register.filter(name="chec_k")
def if_sent(val, arg):
    requests = Friends.objects.filter(
        req_sender=val, req_receiver=arg, sent_status=True)
    return requests.exists()
    # try:
    #     return Friends.objects.filter(req_sender=val, req_receiver=arg)[0].sent_status
    # except:
    #     return False


@register.filter(name="m_type")
def m_type(val):
    return val.media_type()


@register.filter(name="nam_e")
def name(val):
    return val.split("/")[-1].split(".")


@register.filter(name="check_instance")
def check_instance(val):
    return val.__class__.__name__ == "User"


@register.filter()
def status(val, arg):
    if val == arg.creator:
        return "Creator"
    elif val in arg.admins.all():
        return "Admin"
    else:
        return "Member"
