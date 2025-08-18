import uuid
from datetime import datetime
from ..models.message import Message

class MessageManager:
    def __init__(self):
        self.room_messages: dict[str, list[Message]] = {}
        self.MAX_MESSAGES_PER_ROOM = 1000

    def add_message(self, room_id: str, message_type: str, user: str, content: str) -> Message:
        if room_id not in self.room_messages:
            self.room_messages[room_id] = []

        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            user=user,
            message=content,
            timestamp=datetime.now(),
            room_id=room_id
        )

        self.room_messages[room_id].append(message)
        
        # Limita o número de mensagens por sala
        if len(self.room_messages[room_id]) > self.MAX_MESSAGES_PER_ROOM:
            self.room_messages[room_id] = self.room_messages[room_id][-self.MAX_MESSAGES_PER_ROOM:]

        return message

    def get_room_messages(self, room_id: str, limit: int = 50) -> list[Message]:
        messages = self.room_messages.get(room_id, [])
        return messages[-limit:] if messages else []

    def clear_room_messages(self, room_id: str):
        if room_id in self.room_messages:
            del self.room_messages[room_id]
            
    def get_room_message_count(self, room_id: str) -> int:
        return len(self.room_messages.get(room_id, []))

message_manager = MessageManager()