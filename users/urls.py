"""URL for Users"""

from django.urls import path, include
from . import views

app_name = "users"
urlpatterns = [
    path("", include("django.contrib.auth.urls")),
    path("sign_up/", views.sign_up, name="sign_up"),
]
