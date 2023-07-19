from django.contrib.auth.forms import UserCreationForm
from django.forms import PasswordInput

from messengers.models import Info
from django import forms


class NewUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name',
                  'email', "password1", "password2"]
        widgets = {
            "password2": PasswordInput(attrs={"placeholder": "******", "data-toggle": "password"})

        }


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['about', 'bio', 'prof_pics']
