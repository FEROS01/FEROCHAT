from django.urls import path
from . import views

app_name = "messengers"

urlpatterns = [
    path("", views.index, name="index"),
    path("messages/", views.messages, name="messages"),
    path("view_messages/<int:rec_id>/<str:_type>",
         views.view_messages, name="view_messages"),
    path("view_media/<int:rec_id>", views.view_media, name="view_media"),
    path("users/", views.users, name="users"),
    path("user_bio/<int:user_id>", views.user_bio, name="user_bio"),
    path("notifications/", views.notifications, name="notifications"),
    path("send_request/<int:rec_id>", views.send_request, name="send_request"),
    path("cancel_request/<int:rec_id>",
         views.cancel_request, name="cancel_request"),
    path("send_request_bio/<int:rec_id>/<int:bio_id>",
         views.send_request_bio, name="send_request_bio"),
    path("cancel_request_bio/<int:rec_id>/<int:bio_id>",
         views.cancel_request_bio, name="cancel_request_bio"),
    path("accept_request/<int:sen_id>",
         views.accept_request, name="accept_request"),
    path("friends/<int:user_id>", views.friends, name="friends"),
    path("decline_request/<int:sen_id>",
         views.decline_request, name="decline_request"),
    path("delete_message/<int:msg_id>/<int:rec_id>/<str:_type>",
         views.delete_message, name="delete_message"),
    path("unfriend/<int:user_id>/<int:friend_id>",
         views.unfriend, name="unfriend"),
]
