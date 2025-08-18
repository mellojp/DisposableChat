import json
from fastapi import WebSocket
from .room_manager import room_manager 

class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        room_manager.cancel_room_deletion(room_id)

        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(websocket)

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.active_connections:
            self.active_connections[room_id].remove(websocket)
            
            if not self.active_connections[room_id]:
                del self.active_connections[room_id]
                room_manager.schedule_room_deletion(room_id)
    
    async def broadcast(self, payload: dict, room_id: str):
        if room_id in self.active_connections:
            message_str = json.dumps(payload)
            for connection in self.active_connections[room_id]:
                await connection.send_text(message_str)


connection_manager = ConnectionManager()