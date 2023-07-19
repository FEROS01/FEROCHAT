from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import NewUserCreationForm
from django.contrib import messages

# Create your views here.
# Save the info model with any new user


def sign_up(request):
    if request.method != "POST":
        form = NewUserCreationForm()
    else:
        form = NewUserCreationForm(data=request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            messages.success(request, "Account created successfully!")
            return redirect("messengers:index")
    context = {"form": form}
    return render(request, "registration/sign_up.html", context)
