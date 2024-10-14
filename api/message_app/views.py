from django.shortcuts import get_object_or_404
from .models import Message, Group, GroupMessage
from .serializers import (
    MessageListSerializer,
    MessageSerializers,
    ConversationDetailSerializers,
    ConversationListSerializer,
    GroupSerializers,
    GroupMessageSerializer,
    UserSerializers,
)
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    DestroyAPIView,
    UpdateAPIView,
)
from rest_framework.validators import ValidationError
from django.contrib.auth import get_user_model
from response import BaseResponseView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db import models

User = get_user_model()


class CreateMessageView(BaseResponseView, CreateAPIView):
    """View to create a new message between two users"""

    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Automatically assign the sender and create the message."""

        return serializer.save(sender=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = self.perform_create(serializer)
        return self.generate_response(
            status.HTTP_201_CREATED, "Message Sent", MessageSerializers(message).data
        )


class MessageListView(BaseResponseView, ListAPIView):
    """View to list all messages between two users"""

    serializer_class = MessageListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """To retrieve all messages between a user and recieer"""
        user = self.request.user
        receiver_id = self.kwargs.get("receiver_id")

        if user.id == receiver_id:
            raise ValidationError("You cannot have retrieve message with self")
        receiver = get_object_or_404(User, id=receiver_id)

        return Message.objects.filter(
            models.Q(sender=user, receiver=receiver)
            | models.Q(sender=receiver, receiver=user)
        ).order_by("-timestamp")

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return self.generate_response(
            status.HTTP_200_OK, "Messages Successfully retrieved", serializer.data
        )


class MessageDeleteView(BaseResponseView, DestroyAPIView):
    """View to delete a message"""

    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """TO only allow users to delete their own message"""
        return Message.objects.filter(sender=self.request.user)

    def get_object(self):
        message_id = self.kwargs.get("message_id")
        return get_object_or_404(self.get_queryset(), id=message_id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.generate_response(
            status.HTTP_204_NO_CONTENT, "Message succsssfully deleted"
        )


class MessageUpdateView(BaseResponseView, UpdateAPIView):
    """View to update a message"""

    serializer_class = MessageSerializers
    permission_classes = [IsAuthenticated]

    def get_qqueryset(self):
        """TO allow users to update only their messages"""
        return Message.objects.filter(sender=self.request.user)

    def get_object(self):
        """Retrieve the object to be updated"""
        message_id = self.kwargs.get("message_id")
        return get_object_or_404(self.get_queryset(), message_id)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.generate_response(
            status.HTTP_200_OK, "Message successfully updated", serializer.data
        )


class ConversationListView(BaseResponseView, ListAPIView):
    """View to list all conversations between user and other users"""

    serializer_class = UserSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """get a list of users the current user has exchanged messages with"""
        sent_messages = Message.objects.filter(sender=self.request.user).values_list(
            "receiver", flat=True
        )
        received_messages = Message.objects.filter(
            receiver=self.request.user
        ).values_list("sender", flat=True)

        user_ids = set(sent_messages).union(set(received_messages))
        return get_user_model().objects.filter(id__in=user_ids)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        return self.generate_response(
            status.HTTP_200_OK, "Conversations retrieved successfully", serializer.data
        )


class CreateGroupView(BaseResponseView, CreateAPIView):
    """View to create a new group"""

    serializer_class = GroupSerializers
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Automatically assign creator and create the group"""
        return serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = self.perform_create(serializer)

        return self.generate_response(
            status.HTTP_201_CREATED,
            "Group Successfully Created",
            GroupSerializers(group).data,
        )


class CreateGroupMessageView(BaseResponseView, CreateAPIView):
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print(f"User authenticated: {self.request.user.is_authenticated}")
        group_id = self.kwargs.get("group_id")
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise ValidationError("Group not found, it does not exist")

        return serializer.save(sender=self.request.user, group=group.id)

    def create(self, request, *args, **kwargs):
        group_id = self.kwargs.get("group_id")
        # print("erroe comes from here")
        request.data["group"] = group_id
        # print("cause the error comes from here")

        serializer = self.get_serializer(data=request.data)
        print(request.data)
        serializer.is_valid(raise_exception=True)
        group_message = self.perform_create(serializer)

        return self.generate_response(
            status.HTTP_201_CREATED,
            "Group Message sent",
            GroupMessageSerializer(group_message).data,
        )


class GroupMessageUpdateView(BaseResponseView, UpdateAPIView):
    queryset = GroupMessage.objects.all()
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.sender != self.request.user:
            raise PermissionError("You cannot update this message.")
        serializer.save()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return self.generate_response(
            status.HTTP_200_OK, "Group message updated successfully", serializer.data
        )


class GroupMessageListView(BaseResponseView, ListAPIView):
    serializer_class = GroupMessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs["group_id"]
        return GroupMessage.objects.filter(group_id=group_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return self.generate_response(
            status.HTTP_200_OK, "Group messages retrieved successfully", serializer.data
        )


class GroupMessageDeleteView(BaseResponseView, DestroyAPIView):
    queryset = GroupMessage.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = None
    
    def perform_destroy(self, instance):
        if instance.sender != self.request.user:
            raise PermissionError("You cannot delete this message.")
        instance.delete()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return self.generate_response(
            status.HTTP_204_NO_CONTENT, "Group message deleted successfully"
        )
