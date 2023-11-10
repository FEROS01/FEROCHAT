from typing import Any

from django.forms import ModelForm, EmailInput, EmailField

from messengers.models import User, Info


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email')
        widget = {
            "email": EmailInput(attrs={"placeholder": "something@gmail.com"})
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        email_field = self.fields['email']
        email_field.required = True
        email_field.help_text = "Required. Will be used to reset password if forgotten"


class InfoForm(ModelForm):
    class Meta:
        model = Info
        fields = ("bio", "about", 'prof_pics')
