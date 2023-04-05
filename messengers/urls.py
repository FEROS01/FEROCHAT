from django.urls import path
from . import views

app_name = "messengers"

urlpatterns = [
    path("", views.index, name="index"),
    path("messages/", views.messages, name="messages"),
    path("view_messages/<rec_id>", views.view_messages, name="view_messages"),
    path("users/", views.users, name="users"),
    path("user_bio/<int:user_id>", views.user_bio, name="user_bio"),
    # path("profile/<int:user_id>", views.profile, name="profile"),
    path("friend_requests/", views.friend_requests, name="friend_requests"),
    path("send_request/<int:rec_id>", views.send_request, name="send_request"),
]
