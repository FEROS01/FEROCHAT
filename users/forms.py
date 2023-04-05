from django.contrib.auth.forms import UserCreationForm
from messengers.models import Info
from django import forms


class NewUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name',
                  'email']


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['about', 'bio']
