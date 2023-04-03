from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
User=get_user_model


class NewUserCreationForm(UserCreationForm):
    about = 5

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password_1', 'password_2')
