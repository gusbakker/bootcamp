import json

from channels.generic.websocket import AsyncWebsocketConsumer


class MessagerConsumer(AsyncWebsocketConsumer):
    """Consumer to manage WebSocket connections for the Messager app.
    """

    async def connect(self):
        """Consumer Connect implementation, to validate user status and prevent
        non authenticated user to take advante from the connection."""
        print(f"MessagerConsumer: connect() called for user {self.scope['user'].username}")
        if self.scope["user"].is_anonymous:
            # Reject the connection
            print("MessagerConsumer: connection rejected (anonymous)")
            await self.close()

        else:
            # Accept the connection
            print(f"MessagerConsumer: Adding to group {self.scope['user'].username}")
            await self.channel_layer.group_add(
                f"{self.scope['user'].username}", self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        """Consumer implementation to leave behind the group at the moment the
        closes the connection."""
        await self.channel_layer.group_discard(
            f"{self.scope['user'].username}", self.channel_name
        )

    async def receive(self, text_data):
        """Receive method implementation to redirect any new message received
        on the websocket to broadcast to all the clients."""
        await self.send(text_data=json.dumps(text_data))

    async def receive_message(self, event):
        """Receive message from room group."""
        print(f"MessagerConsumer: receive_message() called with event: {event}")
        await self.send(text_data=json.dumps(event))
