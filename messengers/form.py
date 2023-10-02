from collections.abc import Mapping
from typing import Any
from django.core.files.base import File
from django.db.models.base import Model
from django.forms import Textarea, TextInput, FileInput
from django import forms
from django.forms.utils import ErrorList


from .models import Messages


class NewMessage(forms.ModelForm):
    class Meta:
        model = Messages
        fields = ["text", "media"]
        labels = {'text': "", 'media': ""}
        widgets = {
            'text': Textarea(attrs={'placeholder': "message"}),

            # The media field form is manually placed in the view_message.html file
            "media": FileInput(attrs={
                'accept': ".png,.jpeg,.jpg,.mp4,.mp3,.pdf",
                'multiple': True,
            })
        }


class Search(forms.Form):
    search = forms.CharField(max_length=100, label="", label_suffix="", widget=TextInput(
        attrs={"placeholder": "Search", "class": "search"}))


class SearchMessages(forms.Form):

    # The search field form is manually placed in the view_message.html file
    search = forms.CharField(label="", label_suffix="", widget=Textarea(
        attrs={"placeholder": "Search_Messages", "class": "search"}))
