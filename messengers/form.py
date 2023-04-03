from django import forms

from .models import Messages


class NewMessage(forms.ModelForm):
    class Meta:
        model = Messages
        # fields = ["text"]
        exclude = ["date_added", "receiver", "sender"]
        labels = {'text': ""}
