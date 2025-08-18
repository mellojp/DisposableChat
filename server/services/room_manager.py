import uuid
import asyncio
from .message_manager import message_manager

class RoomManager:
    def __init__(self):
        self.active_rooms: set[str] = set()
        self.deletion_timers: dict[str, asyncio.Task] = {}
        self.ROOM_TTL_SECONDS = 120

    def create_room(self) -> str:
        room_id = str(uuid.uuid4().hex)[:10]
        self.active_rooms.add(room_id)
        self.cancel_room_deletion(room_id)
        return room_id

    def list_rooms(self) -> list[str]:
        return list(self.active_rooms)

    def room_exists(self, room_id: str) -> bool:
        return room_id in self.active_rooms

    def remove_room(self, room_id: str):
        if room_id in self.active_rooms:
            self.active_rooms.remove(room_id)
            if room_id in self.deletion_timers:
                del self.deletion_timers[room_id]
            
            # Remove mensagens da sala quando ela é deletada
            message_manager.clear_room_messages(room_id)
            print(f"Room {room_id} was deleted.")

    async def _delete_room_after_delay(self, room_id: str):
        await asyncio.sleep(self.ROOM_TTL_SECONDS)
        if room_id in self.active_rooms:
            self.remove_room(room_id)

    def schedule_room_deletion(self, room_id: str):
        if room_id in self.active_rooms and room_id not in self.deletion_timers:
            task = asyncio.create_task(self._delete_room_after_delay(room_id))
            self.deletion_timers[room_id] = task

    def cancel_room_deletion(self, room_id: str):
        if room_id in self.deletion_timers:
            self.deletion_timers[room_id].cancel()
            del self.deletion_timers[room_id]

room_manager = RoomManager()