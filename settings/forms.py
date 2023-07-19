from messengers.models import User, Info
from django.forms import ModelForm


class ProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email')


class InfoForm(ModelForm):
    class Meta:
        model = Info
        fields = ("bio", "about", 'prof_pics')
