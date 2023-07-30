from messengers.models import User, Info
from django.forms import ModelForm, EmailInput, EmailField


class ProfileForm(ModelForm):
    email = EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email')
        widget = {
            "email": EmailInput(attrs={"required": True, "placeholder": "something@gmail.com"})
        }


class InfoForm(ModelForm):
    class Meta:
        model = Info
        fields = ("bio", "about", 'prof_pics')
