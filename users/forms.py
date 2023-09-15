from typing import Any
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm

from django.forms import PasswordInput, EmailInput
from django import forms

from messengers.models import Info

from .validators import email_exist_validator, email_not_exist_validator


class NewUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name',
                  'email', "password1", "password2"]
        widgets = {
            "password1": PasswordInput(attrs={"placeholder": "******", "data-toggle": "password"}),
            "email": EmailInput(attrs={"placeholder": "something@gmail.com"})

        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        email_field = self.fields['email']
        email_field.required = True
        email_field.help_text = "Required. Will be used to reset password if forgotten"
        email_field.validators.append(email_exist_validator)


class NewPasswordResetForm(PasswordResetForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        email_field = self.fields['email']
        email_field.validators.append(email_not_exist_validator)


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['about', 'bio', 'prof_pics']
