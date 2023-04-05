from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .forms import NewUserCreationForm, InfoForm

# Create your views here.


def sign_up(request):
    if request.method != "POST":
        form = NewUserCreationForm()
    else:
        form = NewUserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return redirect("messengers:index")
    context = {"form": form}
    return render(request, "registration/sign_up.html", context)
