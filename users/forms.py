from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.forms import PasswordInput
from django import forms

from messengers.models import Info, User


class NewUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, help_text="Required. Will be used to reset password if forgotten")

    class Meta(UserCreationForm.Meta):
        fields = ['username', 'first_name', 'last_name',
                  'email', "password1", "password2"]
        widgets = {
            "password2": PasswordInput(attrs={"placeholder": "******", "data-toggle": "password"})

        }


def email_validator(mail):
    users = User.objects.all()
    mails = [user.email for user in users if user.email]
    if mail not in mails:
        raise ValidationError(f"There is no account with this email account")


class NewPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(validators=[email_validator])


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        fields = ['about', 'bio', 'prof_pics']
