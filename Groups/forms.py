from django import forms
from messengers.models import Group, User


class GroupEditForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ('date_created', 'creator', 'admins', 'members')


class SelectMemberForm(forms.Form):
    users = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(choices=[]))

    def __init__(self, *args, **kwargs):
        selected_choices = kwargs.pop("selected_choices")
        super().__init__(*args, **kwargs)
        self.fields["users"].choices = selected_choices


# users = User.objects.all()
# CHOICES = [(user.username, user.username) for user in users]


class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Group
        exclude = ("date_created", "creator", "admins")
        widgets = {
            "members": forms.CheckboxSelectMultiple()
        }
        labels = {
            "description": "Group description",
            "name": "Group name"
        }
