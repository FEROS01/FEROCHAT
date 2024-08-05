from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model as user_model
from django.contrib import messages
from django.http import HttpResponse

from settings.forms import ProfileForm, InfoForm
from messengers.decorators import confirm_htmx_request


@login_required
def settings(request):
    is_dark = request.user.info.dark_theme
    theme = "dark" if is_dark else "light"
    context = {'theme':theme}
    return render(request, "settings/setting.html",context)


def _email_exist_validator(mail):
    """Check if email is already in use"""
    user = user_model().objects.filter(email=mail)
    return user.exists()


@login_required
def edit_prof(request):
    info = request.user.info
    if request.method != "POST":
        prof_form = ProfileForm(instance=request.user)
        info_form = InfoForm(instance=info)
    else:
        prof_form = ProfileForm(
            request.POST, request.FILES, instance=request.user)
        info_form = InfoForm(request.POST, request.FILES, instance=info)
        input_mail = info_form.data['email']
        if input_mail != request.user.email and _email_exist_validator(input_mail):
            prof_form.add_error('email', 'Email has been used')
        if prof_form.is_valid() and info_form.is_valid():
            prof_form.save()
            info_form.save()
            messages.success(request, "Profile updated")
            return redirect("messengers:user_bio", user_id=request.user.id)
    context = {"prof_form": prof_form, "info_form": info_form}
    return render(request, "settings/edit_prof.html", context)


@login_required
def edit_pass(request):
    if request.method != "POST":
        form = PasswordChangeForm(request.user)
    else:
        form = PasswordChangeForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Password change succesful")
            return redirect("settings:setting")
    context = {"form": form}
    return render(request, "settings/edit_pass.html", context)

@login_required
@confirm_htmx_request
def change_theme(request):
    user_id = request.user.id
    user = user_model().objects.get(id=user_id)
    user.info.dark_theme = not user.info.dark_theme
    user.save()
    theme = 'dark' if user.info.dark_theme else 'light'
    return HttpResponse(f'<p class="theme_text">{theme}</p>')

@login_required
@confirm_htmx_request
def file_name(request):
    data = ''
    if request.method == 'POST':
        data = request.FILES['prof_pics'].name
    return HttpResponse(
        f'<div class="name">{data}</div>'
    )
