from django.urls import path
from . import views


urlpatterns = [
    path("create/", views.CreateMessageView.as_view(), name="create_message"),
    path(
        "<uuid:receiver_id>",
        views.MessageListView.as_view(),
        name="message_list",
    ),
    path(
        "<int:message_id>/delete",
        views.MessageDeleteView.as_view(),
        name="message_delete",
    ),
    path(
        "<int:message_id>/update/",
        views.MessageUpdateView.as_view(),
        name="message_update",
    ),
    path(
        "conversations", views.ConversationListView.as_view(), name="conversation_list"
    ),
    path("group/create/", views.CreateGroupView.as_view(), name="create_group"),
    path(
        "group/<uuid:group_id>/message/create/",
        views.CreateGroupMessageView.as_view(),
        name="create_group_message",
    ),
    path(
        "group/<int:group_id>/messages/",
        views.GroupMessageListView.as_view(),
        name="group_message_list",
    ),
    path(
        "group/messages/<int:pk>/delete/",
        views.GroupMessageDeleteView.as_view(),
        name="group_message_delete",
    ),
    path(
        "group-messages/<int:message_id>/update/",
        views.GroupMessageUpdateView.as_view(),
        name="group_message_update",
    ),
]
