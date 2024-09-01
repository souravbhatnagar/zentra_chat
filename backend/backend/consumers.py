import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    """
    ChatConsumer is an asynchronous WebSocket consumer that manages chat functionality.
    It handles the WebSocket connections, message broadcasting within chat rooms, and disconnections.
    """

    async def connect(self):
        """
        Called when a WebSocket connection is established.

        This method retrieves the chat room name from the URL route, constructs a unique group name for
        the chat room, and adds the WebSocket connection to that group. It then accepts the WebSocket
        connection.
        """
        # Retrieve the room name from the URL route parameters
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        # Create a unique group name for the chat room
        self.room_group_name = f"chat_{self.room_name}"

        # Join the chat room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        # Accept the WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the WebSocket connection is closed.

        This method removes the WebSocket connection from the chat room group, ensuring that the user
        is no longer part of the room's broadcast group.

        Parameters:
        close_code (int): The WebSocket close code indicating the reason for the disconnection.
        """
        # Leave the chat room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.

        This method decodes the JSON message from the WebSocket, extracts the actual message content,
        and sends it to the chat room group to be broadcast to all other members of the group.

        Parameters:
        text_data (str): The JSON-encoded message received from the WebSocket.
        """
        # Parse the JSON message received from the WebSocket
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Broadcast the message to the chat room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message", "message": message}
        )

    async def chat_message(self, event):
        """
        Called when a message is received from the chat room group.

        This method sends the received message to the WebSocket, broadcasting it to the client.

        Parameters:
        event (dict): The event dictionary containing the message data. The `type` key indicates
        the type of event (used internally by Channels), and `message` key contains the actual
        chat message.
        """
        # Extract the message from the event
        message = event["message"]

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({"message": message}))
