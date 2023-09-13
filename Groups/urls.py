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
    path("remove_admin/<int:admin_id>/<int:grp_id>",
         views.remove_admin, name="remove_admin"),
    path("exit_group/<int:grp_id>",
         views.exit_group, name="exit_group"),
    path("group_bio/<int:grp_id>", views.group_bio, name="group_bio"),
    path("send_request_bio/<int:rec_id>/<int:bio_id>",
         views.send_request_bio, name="send_request_bio"),
    path("cancel_request_bio/<int:rec_id>/<int:bio_id>",
         views.cancel_request_bio, name="cancel_request_bio"),
    path("view_media/<int:grp_id>", views.view_media, name="view_media"),
]
