# notifications/consumers.py
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

class NotificationsConsumer(AsyncWebsocketConsumer):
    """Consumer to manage WebSocket connections for the Notification app,
    called when the websocket is handshaking as part of initial connection.
    """

    async def connect(self):
        """Consumer Connect implementation, to validate user status and prevent
        non authenticated user to take advante from the connection."""
        logger.info("NotificationsConsumer: connect() called")

        await self.accept() # Accept the connection FIRST

        if self.scope["user"].is_anonymous:
            # Reject the connection AFTER accepting, with a specific code.
            logger.info("NotificationsConsumer: User is anonymous, closing.")
            await self.close(code=4003)  # 4003 Forbidden
        else:
            # Accept the connection
            logger.info("NotificationsConsumer: User is authenticated, adding to group.")
            await self.channel_layer.group_add("notifications", self.channel_name)
            logger.info("NotificationsConsumer: Added to group!")


    async def disconnect(self, close_code):
        """Consumer implementation to leave behind the group at the moment the
        closes the connection."""
        logger.info("NotificationsConsumer: disconnect() called with code: %s", close_code)
        await self.channel_layer.group_discard("notifications", self.channel_name)

    async def receive(self, text_data):
        """Receive method implementation to redirect any new message received
        on the websocket to broadcast to all the clients."""
        logger.info("NotificationsConsumer: receive() called with data: %s", text_data)
        await self.send(text_data=json.dumps(text_data))

    async def send_notification(self, event):
        """ Send notification to WebSocket """
        logger.info("NotificationsConsumer: send_notification called with event: %s", event)
        await self.send(text_data=json.dumps(event["text"]))