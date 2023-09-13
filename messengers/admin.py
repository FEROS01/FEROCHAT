from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Messages, Info, Friends  # , Group, Membership
from django.contrib.auth.models import User
# Register your models here.

admin.site.register(Messages)
admin.site.register(Friends)
# admin.site.register(Group)
# admin.site.register(Membership)


# Define an inline admin descriptor for Info model
# which acts a bit like a singleton


class InfoInline(admin.StackedInline):
    model = Info
    can_delete = False
    verbose_name_plural = 'Infos'


# Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (InfoInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
