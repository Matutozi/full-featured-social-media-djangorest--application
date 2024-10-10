import base64
import json
import secrets
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from django.core.files.base import ContentFile
from django.contrib.auth.models import AnonymousUser

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("WebSocket connected")

        self.user = self.scope["user"]
        
        #print(self.user)
        #xprint(self.user.username)

        self.user_id = self.scope["url_route"]["kwargs"].get("user_id")
        self.group_id = self.scope["url_route"]["kwargs"].get("group_id")

        if self.user_id:
            self.room_group_name = f"chat_{self.user.id}"
        elif self.group_id:
            self.room_group_name = f"group_chat_{self.group_id}"
        else:
            print("Input the correct ID")
            self.close()

        print(self.room_group_name)

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()
        print(f"WebSocket connected and joined room: {self.room_group_name}")

        #self.send_past_messages()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

        print(f"Disconnected from room: {self.room_group_name}")

    # Receive message from WebSocket
    def receive(self, text_data=None, bytes_data=None):
        # Parse the JSON data into a dictionary object
        text_data_json = json.loads(text_data)

        if self.group_id:
            chat_type = {"type": "group_chat_message"}
        else:
            chat_type = {"type": "chat_message"}

        # Send message to room group
        return_dict = {**chat_type, **text_data_json}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            return_dict,
        )

    def chat_message(self, event: dict) -> None:
        print("Incoming individual message event:", event)
        self.handle_message(event, individual=True)

    def group_chat_message(self, event: dict) -> None:
        print("Incoming group message event:", event)
        self.handle_message(event, individual=False)

    def handle_message(self, event: dict, individual: bool) -> None:

        from users.models import User
        from .models import Message, GroupMessage, Group
        from .serializers import (
            MessageSerializers,
            GroupMessageSerializer,
        )

        print("Incoming event:", event)

        text_data_json = event.copy()
        text_data_json.pop("type", None)

        message = text_data_json.get("message")
        attachment = text_data_json.get("attachment")
        receiver_id = text_data_json.get("receiver_id")
        if receiver_id is not None:
            receiver_id = str(receiver_id)
        sender = self.scope["user"]

        if not sender.is_authenticated:
            print("User is not authenticated")
            return

        if individual:
            try:
                #print(dir(sender))
                sender = get_user_model().objects.get(id=sender.id)
            except User.DoesNotExist:
                print(f"User with id {sender.id} does not exist.")
                return

            # Check if receiver_id is provided
            if receiver_id is None:
                print("No receiver ID provided.")
                return

            try:
                receiver = get_user_model().objects.get(id=receiver_id)
            except User.DoesNotExist:
                print(f"Receiver with id {receiver_id} does not exist.")
                return

            if attachment:
                file_str, file_ext = attachment["data"], attachment["format"]
                file_data = ContentFile(
                    base64.b64decode(file_str),
                    name=f"{secrets.token_hex(8)}.{file_ext}",
                )
                _message = Message.objects.create(
                    sender=sender,
                    receiver=receiver,  # Add receiver to the message creation
                    attachment=file_data,
                    text=message,
                )
            else:
                _message = Message.objects.create(
                    sender=sender,
                    receiver=receiver,  # Add receiver to the message creation
                    text=message,
                )

            print(
                f"Message created: Sender {sender.id}, Receiver {receiver.id}, Text: {message}"
            )

            serializer = MessageSerializers(instance=_message)

            response_data = serializer.data
            response_data['sender'] = str(response_data['sender'])
            response_data['receiver'] = str(response_data['receiver'])
            self.send(text_data=json.dumps(response_data))

        else:
            if not Group.objects.filter(id=self.group_id, members=sender).exists():
                self.send(
                    text_data=json.dumps(
                        {"error": "You are not a member of this group."}
                    )
                )
                return
            try:

                group_message = GroupMessage.objects.create(
                    sender=sender,
                    group_id=self.group_id,
                    text=message,
                    attachment=attachment,
                )
                serializer = GroupMessageSerializer(instance=group_message)
                self.send(text_data=json.dumps(serializer.data))
                print(
                    f"Group Message created: Sender {sender.id}, Group {self.group_id}, Text: {message}"
                )
            except Exception as e:
                print(f"Error creating group message: {str(e)}")
                self.send(text_data=json.dumps({"error": str(e)}))

    def send_past_messages(self):
        from .models import Message, GroupMessage
        from .serializers import (
            MessageSerializers,
            GroupMessageSerializer,
        )

        if self.group_id:
            messages = GroupMessage.objects.filter(group_id=self.group_id).order_by(
                "timestamp"
            )
            serializer = GroupMessageSerializer(messages, many=True)
        else:
            # Fetch past individual messages
            messages = Message.objects.filter(
                receiver=self.user.id, sender=self.user.id
            ).order_by("timestamp")
            serializer = MessageSerializers(messages, many=True)

        self.send(text_data=json.dumps(serializer.data))
