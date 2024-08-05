from django.urls import path
from . import views

app_name = "settings"

urlpatterns = [
    path("", views.settings, name="setting"),
    path("edit_prof/", views.edit_prof, name="edit_prof"),
    path("edit_pass/", views.edit_pass, name="edit_pass"),
    path("file_name/", views.file_name, name="file_name"),
    path("change_theme/", views.change_theme, name="change_theme")
]
