"""URL for Users"""

from django.urls import path, include
from . import views
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from .forms import NewPasswordResetForm

app_name = "users"
urlpatterns = [

    path("sign_up/", views.sign_up, name="sign_up"),
    path('password_reset/', PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        form_class=NewPasswordResetForm), name='password_reset'),
    path("", include("django.contrib.auth.urls")),
]
