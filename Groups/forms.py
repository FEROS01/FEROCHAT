from django import forms
from Groups.models import Group


class GroupEditForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'prof_pics']


class SelectMemberForm(forms.Form):
    users = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(choices=[]), required=False)
    admins = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple(choices=[]), required=False)

    def __init__(self, *args, **kwargs):
        selected_choices = kwargs.pop("selected_choices")
        selected_admin_choices = kwargs.pop("selected_admin_choices")
        super().__init__(*args, **kwargs)
        self.fields["users"].choices = selected_choices
        self.fields["admins"].choices = selected_admin_choices


class GroupCreationForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description', 'prof_pics', 'members']
        widgets = {
            "members": forms.CheckboxSelectMultiple()
        }
        labels = {
            "description": "Group description",
            "name": "Group name"
        }
