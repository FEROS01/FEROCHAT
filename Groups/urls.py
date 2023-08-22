from django.urls import path, include
from . import views

app_name = "Groups"
urlpatterns = [
    path("create_group/", views.create_group, name="create_group"),
    path("edit_group/<int:grp_id>",
         views.edit_group, name="edit_group"),
    path("remove_user/<int:user_id>/<int:grp_id>",
         views.remove_user, name="remove_user"),
    path("select_member/<int:grp_id>", views.select_member, name="select_member"),
]
