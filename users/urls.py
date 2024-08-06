"""URL for Users"""
from django.contrib.auth.views import PasswordResetView, LoginView
from django.urls import path, include

from .forms import NewPasswordResetForm

from . import views


app_name = "users"
urlpatterns = [

    path("sign_up/", views.sign_up, name="sign_up"),
    path('password_reset/', PasswordResetView.as_view(
        html_email_template_name='registration/password_reset_email.html',
        email_template_name='registration/password_reset_email.html',
        template_name='registration/password_reset_form.html',
        form_class=NewPasswordResetForm), name='password_reset'),
    path("", include("django.contrib.auth.urls")),
]
